import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                           QLabel, QHBoxLayout, QTextEdit, QGroupBox, QLineEdit, 
                           QCheckBox, QSpinBox, QComboBox, QTabWidget, QListWidget,
                           QSplitter, QDialog, QDialogButtonBox, QFormLayout, QScrollArea,
                           QProgressBar, QMessageBox, QFileDialog, QMenuBar, QAction,
                           QSystemTrayIcon, QMenu, QShortcut, QToolTip, QDockWidget,
                           QDesktopWidget, QFrame)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal, QThread, pyqtSlot, QSettings, QRect
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont, QKeySequence, QIcon
import pytesseract
import pyperclip
from PIL import Image
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import json
import sounddevice as sd
import tempfile
import requests
import wave
import re
import logging
import traceback
from pathlib import Path


class FloatingResponseWindow(QMainWindow):
    """Плавающее окно для быстрых ответов"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💬 Quick Responses")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # Не удалять при закрытии
        
        # Устанавливаем размер и позицию
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        self.setGeometry(screen_rect.width() - 500, 100, 480, 400)
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Заголовок
        title_label = QLabel("💬 Quick Responses")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Поле для ввода вопроса
        question_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Enter question to generate quick responses...")
        self.question_input.returnPressed.connect(self.generate_responses_signal)
        question_layout.addWidget(self.question_input)
        
        self.generate_btn = QPushButton("🚀 Generate")
        self.generate_btn.clicked.connect(self.generate_responses_signal)
        question_layout.addWidget(self.generate_btn)
        
        layout.addLayout(question_layout)
        
        # Статус генерации
        self.status_label = QLabel("Ready to generate responses...")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Русский ответ
        ru_group = QGroupBox("🇷🇺 Russian Response")
        ru_layout = QVBoxLayout()
        
        self.ru_response_area = QTextEdit()
        self.ru_response_area.setMaximumHeight(120)
        self.ru_response_area.setFont(QFont("Consolas", 10))
        self.ru_response_area.setPlaceholderText("Русский ответ появится здесь...")
        self.ru_response_area.setStyleSheet("QTextEdit { background-color: #f8f9fa; border: 1px solid #dee2e6; }")
        ru_layout.addWidget(self.ru_response_area)
        
        ru_buttons = QHBoxLayout()
        copy_ru_btn = QPushButton("📋 Copy RU")
        copy_ru_btn.clicked.connect(self.copy_ru_response)
        copy_ru_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; }")
        ru_buttons.addWidget(copy_ru_btn)
        ru_buttons.addStretch()
        ru_layout.addLayout(ru_buttons)
        
        ru_group.setLayout(ru_layout)
        layout.addWidget(ru_group)
        
        # Английский ответ
        en_group = QGroupBox("🇺🇸 English Response")
        en_layout = QVBoxLayout()
        
        self.en_response_area = QTextEdit()
        self.en_response_area.setMaximumHeight(120)
        self.en_response_area.setFont(QFont("Consolas", 10))
        self.en_response_area.setPlaceholderText("English response will appear here...")
        self.en_response_area.setStyleSheet("QTextEdit { background-color: #f8f9fa; border: 1px solid #dee2e6; }")
        en_layout.addWidget(self.en_response_area)
        
        en_buttons = QHBoxLayout()
        copy_en_btn = QPushButton("📋 Copy EN")
        copy_en_btn.clicked.connect(self.copy_en_response)
        copy_en_btn.setStyleSheet("QPushButton { background-color: #007bff; color: white; }")
        en_buttons.addWidget(copy_en_btn)
        en_buttons.addStretch()
        en_layout.addLayout(en_buttons)
        
        en_group.setLayout(en_layout)
        layout.addWidget(en_group)
        
        # Кнопки управления окном
        control_layout = QHBoxLayout()
        
        self.pin_btn = QPushButton("📌 Pin")
        self.pin_btn.setCheckable(True)
        self.pin_btn.toggled.connect(self.toggle_pin)
        self.pin_btn.setToolTip("Закрепить окно поверх всех")
        control_layout.addWidget(self.pin_btn)
        
        self.minimize_btn = QPushButton("➖ Minimize")
        self.minimize_btn.clicked.connect(self.showMinimized)
        control_layout.addWidget(self.minimize_btn)
        
        control_layout.addStretch()
        
        self.close_btn = QPushButton("❌ Close")
        self.close_btn.clicked.connect(self.hide)
        self.close_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
        control_layout.addWidget(self.close_btn)
        
        layout.addLayout(control_layout)
        
    def generate_responses_signal(self):
        """Сигнал для генерации ответов"""
        self.generate_responses_requested.emit(self.question_input.text())
        
    generate_responses_requested = pyqtSignal(str)
    
    def set_responses(self, ru_text, en_text):
        """Установить сгенерированные ответы"""
        self.ru_response_area.setText(ru_text)
        self.en_response_area.setText(en_text)
        self.status_label.setText("✅ Responses generated successfully!")
        
    def set_status(self, status):
        """Установить статус"""
        self.status_label.setText(status)
        
    def set_question(self, question):
        """Установить вопрос"""
        self.question_input.setText(question)
        
    def copy_ru_response(self):
        """Копировать русский ответ"""
        text = self.ru_response_area.toPlainText()
        if text:
            pyperclip.copy(text)
            self.status_label.setText("📋 Russian response copied!")
            
    def copy_en_response(self):
        """Копировать английский ответ"""
        text = self.en_response_area.toPlainText()
        if text:
            pyperclip.copy(text)
            self.status_label.setText("📋 English response copied!")
            
    def toggle_pin(self, checked):
        """Переключить закрепление окна"""
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📌 Pinned")
            self.pin_btn.setStyleSheet("QPushButton { background-color: #ffc107; }")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📌 Pin")
            self.pin_btn.setStyleSheet("")
        self.show()
        
    def closeEvent(self, event):
        """Переопределяем закрытие - просто скрываем"""
        event.ignore()
        self.hide()


class FloatingAudioWindow(QMainWindow):
    """Плавающее окно для аудио транскрипции"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎤 Audio Transcription")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        
        # Устанавливаем размер и позицию
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        self.setGeometry(50, 100, 600, 500)
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Заголовок с контролами записи
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🎤 Audio Transcription")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.record_btn = QPushButton("🎤 Start Recording")
        self.record_btn.setStyleSheet("QPushButton { font-size: 14px; padding: 8px; }")
        self.record_btn.clicked.connect(self.toggle_recording_signal)
        header_layout.addWidget(self.record_btn)
        
        layout.addLayout(header_layout)
        
        # Статус записи
        self.status_label = QLabel("Ready to record")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Транскрипция в реальном времени
        transcription_group = QGroupBox("📢 Real-time Transcription")
        transcription_layout = QVBoxLayout()
        
        self.transcription_area = QTextEdit()
        self.transcription_area.setFont(QFont("Consolas", 11))
        self.transcription_area.setPlaceholderText("Транскрипция аудио появится здесь...")
        self.transcription_area.setStyleSheet("QTextEdit { background-color: #f0f0f0; border: 1px solid #ccc; }")
        transcription_layout.addWidget(self.transcription_area)
        
        transcription_group.setLayout(transcription_layout)
        layout.addWidget(transcription_group)
        
        # Обработанный текст
        processed_group = QGroupBox("🤖 Processed Text")
        processed_layout = QVBoxLayout()
        
        self.processed_area = QTextEdit()
        self.processed_area.setFont(QFont("Consolas", 11))
        self.processed_area.setPlaceholderText("Обработанный текст появится здесь...")
        self.processed_area.setStyleSheet("QTextEdit { background-color: #e8f5e8; border: 1px solid #28a745; }")
        processed_layout.addWidget(self.processed_area)
        
        processed_buttons = QHBoxLayout()
        copy_audio_btn = QPushButton("📋 Copy Audio")
        copy_audio_btn.clicked.connect(self.copy_processed_text)
        copy_audio_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; }")
        processed_buttons.addWidget(copy_audio_btn)
        
        save_audio_btn = QPushButton("💾 Save Audio")
        save_audio_btn.clicked.connect(self.save_audio_text_signal)
        processed_buttons.addWidget(save_audio_btn)
        
        processed_buttons.addStretch()
        processed_layout.addLayout(processed_buttons)
        
        processed_group.setLayout(processed_layout)
        layout.addWidget(processed_group)
        
        # Кнопки управления окном
        control_layout = QHBoxLayout()
        
        self.pin_btn = QPushButton("📌 Pin")
        self.pin_btn.setCheckable(True)
        self.pin_btn.toggled.connect(self.toggle_pin)
        control_layout.addWidget(self.pin_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_all_text)
        control_layout.addWidget(self.clear_btn)
        
        control_layout.addStretch()
        
        self.close_btn = QPushButton("❌ Close")
        self.close_btn.clicked.connect(self.hide)
        self.close_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
        control_layout.addWidget(self.close_btn)
        
        layout.addLayout(control_layout)
        
    toggle_recording_requested = pyqtSignal()
    save_audio_text_requested = pyqtSignal()
    
    def toggle_recording_signal(self):
        """Сигнал для переключения записи"""
        self.toggle_recording_requested.emit()
        
    def save_audio_text_signal(self):
        """Сигнал для сохранения аудио текста"""
        self.save_audio_text_requested.emit()
        
    def set_recording_state(self, is_recording):
        """Установить состояние записи"""
        if is_recording:
            self.record_btn.setText("⏹️ Stop Recording")
            self.record_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; font-size: 14px; padding: 8px; }")
            self.status_label.setText("🔴 Recording...")
        else:
            self.record_btn.setText("🎤 Start Recording")
            self.record_btn.setStyleSheet("QPushButton { font-size: 14px; padding: 8px; }")
            self.status_label.setText("Ready to record")
            
    def add_transcription(self, text):
        """Добавить транскрипцию"""
        self.transcription_area.append(text)
        
    def add_processed_text(self, text):
        """Добавить обработанный текст"""
        self.processed_area.append(text)
        
    def set_status(self, status):
        """Установить статус"""
        self.status_label.setText(status)
        
    def copy_processed_text(self):
        """Копировать обработанный текст"""
        text = self.processed_area.toPlainText()
        if text:
            pyperclip.copy(text)
            self.status_label.setText("📋 Processed text copied!")
            
    def clear_all_text(self):
        """Очистить весь текст"""
        self.transcription_area.clear()
        self.processed_area.clear()
        self.status_label.setText("Text cleared")
        
    def toggle_pin(self, checked):
        """Переключить закрепление окна"""
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📌 Pinned")
            self.pin_btn.setStyleSheet("QPushButton { background-color: #ffc107; }")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📌 Pin")
            self.pin_btn.setStyleSheet("")
        self.show()
        
    def closeEvent(self, event):
        """Переопределяем закрытие - просто скрываем"""
        event.ignore()
        self.hide()


class StatusWidget(QWidget):
    """Улучшенный виджет статуса с прогресс-баром"""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
    def show_message(self, message, duration=0):
        self.status_label.setText(message)
        if duration > 0:
            QTimer.singleShot(duration * 1000, lambda: self.status_label.setText("Ready"))
            
    def show_progress(self, message, progress=None):
        self.status_label.setText(message)
        if progress is not None:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)
            
    def hide_progress(self):
        self.progress_bar.setVisible(False)


class OCRWorker(QThread):
    result_ready = pyqtSignal(str, str, str)  # raw_text, processed_text, content_type
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)  # progress percentage
    
    def __init__(self, image, use_openai=False, api_key=None, model='gpt-4o', interview_mode=False):
        super().__init__()
        self.image = image
        self.use_openai = use_openai
        self.api_key = api_key
        self.model = model
        self.interview_mode = interview_mode
        self.cancelled = False
        
    def cancel(self):
        self.cancelled = True
        
    def classify_content(self, text, interview_mode=False):
        """Определяет тип контента: вопрос, задача или обычный текст"""
        text_lower = text.lower().strip()
        
        if interview_mode:
            # Специальная логика для собеседований
            
            # Алгоритмические задачи
            algo_keywords = [
                'algorithm', 'complexity', 'o(', 'big o', 'sort', 'search', 'tree', 'graph', 'array', 'list',
                'алгоритм', 'сложность', 'сортировка', 'поиск', 'дерево', 'граф', 'массив',
                'binary search', 'dfs', 'bfs', 'dynamic programming', 'recursion', 'fibonacci', 'factorial'
            ]
            if any(keyword in text_lower for keyword in algo_keywords):
                return "algorithm"
                
            # Код-ревью
            code_patterns = [
                r'def\s+\w+', r'function\s+\w+', r'class\s+\w+', r'for\s+\w+\s+in', r'while\s*\(',
                r'if\s*\(', r'return\s', r'import\s', r'#.*', r'//.*', r'/\*.*\*/'
            ]
            if any(re.search(pattern, text) for pattern in code_patterns):
                return "code_review"
                
            # Логические задачи
            logic_keywords = [
                'logic', 'puzzle', 'riddle', 'brain teaser', 'probability', 'combinatorics',
                'логика', 'головоломка', 'загадка', 'вероятность', 'комбинаторика'
            ]
            if any(keyword in text_lower for keyword in logic_keywords):
                return "logic_puzzle"
                
            # Математические задачи для программистов
            math_prog_keywords = [
                'time complexity', 'space complexity', 'leetcode', 'hackerrank', 'codewars',
                'временная сложность', 'пространственная сложность'
            ]
            if any(keyword in text_lower for keyword in math_prog_keywords):
                return "programming_task"
        
        # Обычная логика
        # Определяем вопросы
        question_indicators = ['?', 'что', 'как', 'где', 'когда', 'почему', 'зачем', 'кто', 'чем', 'what', 'how', 'where', 'when', 'why', 'who', 'which']
        if any(indicator in text_lower for indicator in question_indicators):
            return "question"
            
        # Определяем задачи/примеры
        task_indicators = ['решить', 'найти', 'вычислить', 'определить', 'calculate', 'solve', 'find', '=', '+', '-', '*', '/', 'x²', '²', '³', '∫', '∑']
        if any(indicator in text_lower for indicator in task_indicators):
            return "task"
            
        # Определяем математические выражения
        math_patterns = [r'\d+\s*[+\-*/]\s*\d+', r'\d+\s*=', r'[a-z]\s*=', r'\(.*\)', r'\d+x', r'x\d+']
        for pattern in math_patterns:
            if re.search(pattern, text_lower):
                return "task"
                
        return "text"
        
    def process_with_ai(self, text, content_type, interview_mode=False):
        """Обработка текста с помощью OpenAI в зависимости от типа контента"""
        if self.cancelled:
            return text
            
        client = OpenAI(api_key=self.api_key)
        
        if interview_mode:
            # Специальные промпты для собеседований
            if content_type == "algorithm":
                system_prompt = """Ты эксперт-помощник по алгоритмам на собеседовании. Дай полное решение алгоритмической задачи:
                1. Анализ задачи и понимание требований
                2. Подход к решению (брут-форс, оптимизация)
                3. Код на Python/JavaScript/Java (по выбору)
                4. Временная сложность O(n)
                5. Пространственная сложность
                6. Крайние случаи и тестирование
                7. Альтернативные подходы"""
                user_prompt = f"Реши эту алгоритмическую задачу как на собеседовании: {text}"
                
            elif content_type == "code_review":
                system_prompt = """Ты эксперт по код-ревью. Проанализируй код и дай полный отчет:
                1. Ошибки и баги
                2. Проблемы производительности
                3. Нарушения лучших практик
                4. Проблемы читаемости
                5. Предложения по улучшению
                6. Исправленная версия кода (если нужно)"""
                user_prompt = f"Проведи код-ревью этого кода: {text}"
                
            elif content_type == "logic_puzzle":
                system_prompt = """Ты эксперт по логическим задачам на собеседованиях. Реши логическую задачу:
                1. Понимание условий задачи
                2. Логические рассуждения пошагово
                3. Альтернативные подходы (если есть)
                4. Объяснение логики решения"""
                user_prompt = f"Реши эту логическую задачу как на собеседовании: {text}"
                
            elif content_type == "programming_task":
                system_prompt = """Ты эксперт-программист на собеседовании. Реши программистскую задачу:
                1. Понимание требований
                2. План решения и алгоритм
                3. Код с комментариями
                4. Оптимизация и сложность
                5. Тестовые случаи
                6. Обработка ошибок
                Покажи мышление как на реальном собеседовании."""
                user_prompt = f"Реши эту программистскую задачу как на собеседовании: {text}"
                
            else:  # обычный текст в режиме собеседования
                system_prompt = """Ты помощник на собеседовании. Помоги понять и объяснить любые вопросы, связанные с программированием, технологиями, архитектурой. 
                Дай полные, практические ответы с примерами."""
                user_prompt = f"Объясни это как на собеседовании: {text}"
        
        else:
            # Обычная логика
            if content_type == "question":
                system_prompt = """Ты помощник, который отвечает на вопросы. Дай точный, информативный и полезный ответ на вопрос. 
                Если это учебный вопрос, объясни решение пошагово. Отвечай на том же языке, что и вопрос."""
                user_prompt = f"Ответь на этот вопрос: {text}"
                
            elif content_type == "task":
                system_prompt = """Ты помощник для решения задач. Реши задачу пошагово, покажи все вычисления. 
                Если это математическая задача, проверь правильность решения. Объясни каждый шаг.
                Отвечай на том же языке, что и задача."""
                user_prompt = f"Реши эту задачу: {text}"
                
            else:  # обычный текст
                system_prompt = """Ты помощник для обработки текста. Исправь ошибки OCR, улучши форматирование, 
                сделай текст более читаемым. Сохрани исходный смысл и язык текста."""
                user_prompt = f"Исправь и отформатируй этот текст: {text}"
            
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()
        
    def run(self):
        try:
            self.progress_updated.emit(10)
            if self.cancelled:
                return
                
            # Улучшенные настройки Tesseract для лучшего распознавания
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя .,!?()[]{}":;+-=*/\\|_@#$%^&<>~`'
            
            # Пробуем разные PSM режимы для лучшего результата
            psm_modes = [6, 8, 7, 13]  # Разные режимы сегментации страницы
            best_text = ""
            best_confidence = 0
            
            for psm in psm_modes:
                try:
                    config = f'--oem 3 --psm {psm}'
                    
                    # Получаем текст и данные о достоверности
                    data = pytesseract.image_to_data(self.image, config=config, output_type=pytesseract.Output.DICT)
                    text = pytesseract.image_to_string(self.image, config=config)
                    
                    # Вычисляем среднюю достоверность
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Используем текст с наивысшей достоверностью
                    if avg_confidence > best_confidence and text.strip():
                        best_confidence = avg_confidence
                        best_text = text.strip()
                        
                except Exception:
                    continue
            
            # Если ни один режим не дал хорошего результата, используем базовый
            if not best_text:
                try:
                    raw_text = pytesseract.image_to_string(self.image, config='--oem 3 --psm 6')
                except Exception:
                    raw_text = pytesseract.image_to_string(self.image)
            else:
                raw_text = best_text
                
            raw_text = raw_text.strip()
            
            # Дополнительная очистка текста
            if raw_text:
                # Удаляем лишние пробелы и переносы строк
                raw_text = ' '.join(raw_text.split())
                # Убираем очевидно неправильные символы
                raw_text = ''.join(char for char in raw_text if ord(char) < 65536)
            
            self.progress_updated.emit(40)
            if self.cancelled:
                return
            
            if not raw_text:
                self.result_ready.emit("", "", "text")
                return
                
            content_type = self.classify_content(raw_text, self.interview_mode)
            
            self.progress_updated.emit(60)
            if self.cancelled:
                return
            
            if self.use_openai and self.api_key:
                try:
                    processed_text = self.process_with_ai(raw_text, content_type, self.interview_mode)
                    self.progress_updated.emit(100)
                    self.result_ready.emit(raw_text, processed_text, content_type)
                except Exception as e:
                    self.error_occurred.emit(f"OpenAI Error: {str(e)}")
                    self.result_ready.emit(raw_text, raw_text, content_type)
            else:
                self.progress_updated.emit(100)
                self.result_ready.emit(raw_text, raw_text, content_type)
                
        except Exception as e:
            self.error_occurred.emit(f"OCR Error: {str(e)}")


class AudioCaptureWorker(QThread):
    audio_captured = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recording = False
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_duration = 3  # seconds
        
    def start_recording(self):
        self.recording = True
        self.start()
        
    def stop_recording(self):
        self.recording = False
        
    def run(self):
        try:
            chunk_size = self.sample_rate * self.chunk_duration
            
            while self.recording:
                # Записываем аудио chunk
                audio_data = sd.rec(chunk_size, samplerate=self.sample_rate, 
                                  channels=self.channels, dtype=np.int16)
                sd.wait()  # Ждем завершения записи
                
                if self.recording:  # Проверяем, что все еще записываем
                    # Конвертируем в bytes
                    audio_bytes = audio_data.tobytes()
                    self.audio_captured.emit(audio_bytes)
                    
        except Exception as e:
            self.error_occurred.emit(f"Audio capture error: {str(e)}")


class TranscriptionWorker(QThread):
    transcription_ready = pyqtSignal(str, str)  # original_text, processed_text
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, audio_data, settings, user_name=""):
        super().__init__()
        self.audio_data = audio_data
        self.settings = settings
        self.user_name = user_name
        self.cancelled = False
        
    def cancel(self):
        self.cancelled = True
        
    def save_audio_temp(self, audio_data):
        """Сохраняет аудио во временный файл"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        
        # Конвертируем bytes обратно в numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Сохраняем в WAV формат
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bit = 2 bytes
            wf.setframerate(16000)
            wf.writeframes(audio_data)
        
        return temp_file.name
        
    def run(self):
        try:
            self.progress_updated.emit(20)
            if self.cancelled:
                return
                
            # Сохраняем аудио во временный файл
            temp_audio_file = self.save_audio_temp(self.audio_data)
            
            self.progress_updated.emit(40)
            if self.cancelled:
                os.unlink(temp_audio_file)
                return
            
            # Используем OpenAI Whisper для транскрипции
            client = OpenAI(api_key=self.settings.get('api_key', ''))
            
            with open(temp_audio_file, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=self.settings.get('whisper_language', 'auto') if self.settings.get('whisper_language', 'auto') != 'auto' else None
                )
                
            self.progress_updated.emit(70)
            if self.cancelled:
                os.unlink(temp_audio_file)
                return
                
            original_text = transcript.text.strip()
            
            if not original_text:
                os.unlink(temp_audio_file)
                return
                
            # Обрабатываем текст с помощью GPT
            processed_text = self.process_transcription(original_text)
            
            self.progress_updated.emit(100)
            self.transcription_ready.emit(original_text, processed_text)
            
            # Удаляем временный файл
            os.unlink(temp_audio_file)
            
        except Exception as e:
            self.error_occurred.emit(f"Transcription error: {str(e)}")
            
    def process_transcription(self, text):
        """Обрабатывает транскрипцию через GPT"""
        if self.cancelled:
            return text
            
        if not self.settings.get('use_openai', False) or not self.settings.get('api_key'):
            return text
            
        try:
            client = OpenAI(api_key=self.settings.get('api_key'))
            
            # Определяем, есть ли имя пользователя в тексте
            user_mentioned = self.user_name and self.user_name.lower() in text.lower()
            
            # Выбираем промпт в зависимости от настроек
            if user_mentioned:
                system_prompt = f"""
                Ты помощник для обработки текста с конференций. В тексте упоминается имя пользователя "{self.user_name}", 
                что означает, что к нему обращаются с вопросом или задачей.
                
                Твоя задача:
                1. Переведи и отформатируй текст по запросу пользователя
                2. Если в тексте есть вопрос к {self.user_name}, подготовь краткие варианты ответов
                3. Выдели ключевые моменты
                
                Промпт пользователя: {self.settings.get('audio_prompt', 'Переведи текст и сделай его более читаемым')}
                """
            else:
                system_prompt = f"""
                Ты помощник для обработки текста с конференций. 
                
                Промпт пользователя: {self.settings.get('audio_prompt', 'Переведи текст и сделай его более читаемым')}
                """
                
            response = client.chat.completions.create(
                model=self.settings.get('model', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Обработай этот текст: {text}"}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Ошибка обработки: {str(e)}\n\nОригинальный текст: {text}"


class QuickResponseWorker(QThread):
    response_ready = pyqtSignal(str, str)  # ru_response, en_response
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, question, settings, user_name=""):
        super().__init__()
        self.question = question
        self.settings = settings
        self.user_name = user_name
        self.cancelled = False
        
    def cancel(self):
        self.cancelled = True
        
    def run(self):
        try:
            client = OpenAI(api_key=self.settings.get('api_key'))
            
            system_prompt = f"""
            Ты помощник {self.user_name if self.user_name else 'пользователя'} на конференции. 
            Дай КРАТКИЙ (1-2 предложения) но информативный ответ на заданный вопрос.
            
            Отвечай профессионально и по делу. Если нужны уточнения, укажи это.
            """
            
            self.progress_updated.emit(30)
            if self.cancelled:
                return
            
            # Генерируем ответ на русском
            ru_response = client.chat.completions.create(
                model=self.settings.get('model', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": system_prompt + " Отвечай на русском языке."},
                    {"role": "user", "content": self.question}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            self.progress_updated.emit(65)
            if self.cancelled:
                return
            
            # Генерируем ответ на английском
            en_response = client.chat.completions.create(
                model=self.settings.get('model', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": system_prompt + " Respond in English."},
                    {"role": "user", "content": self.question}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            self.progress_updated.emit(100)
            
            ru_text = ru_response.choices[0].message.content.strip()
            en_text = en_response.choices[0].message.content.strip()
            
            self.response_ready.emit(ru_text, en_text)
            
        except Exception as e:
            self.error_occurred.emit(f"Response generation error: {str(e)}")


class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки - Complete Assistant")
        self.setModal(True)
        self.settings = settings or {}
        self.setMinimumSize(600, 700)
        
        layout = QFormLayout()
        
        # OpenAI настройки
        openai_group = QGroupBox("OpenAI Настройки")
        openai_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.settings.get('api_key', ''))
        openai_layout.addRow("OpenAI API Key:", self.api_key_input)
        
        # Кнопка тестирования API
        self.test_api_button = QPushButton("🔍 Тест API")
        self.test_api_button.clicked.connect(self.test_api_connection)
        openai_layout.addRow("", self.test_api_button)
        
        self.use_openai_checkbox = QCheckBox("Использовать OpenAI для обработки")
        self.use_openai_checkbox.setChecked(self.settings.get('use_openai', False))
        openai_layout.addRow(self.use_openai_checkbox)
        
        self.model_combo = QComboBox()
        models = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']
        self.model_combo.addItems(models)
        self.model_combo.setCurrentText(self.settings.get('model', 'gpt-4o'))
        openai_layout.addRow("OpenAI Model:", self.model_combo)
        
        openai_group.setLayout(openai_layout)
        layout.addRow(openai_group)
        
        # OCR настройки
        ocr_group = QGroupBox("OCR Настройки")
        ocr_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(['eng', 'rus', 'eng+rus', 'deu', 'fra', 'spa', 'ita'])
        self.language_combo.setCurrentText(self.settings.get('ocr_language', 'eng'))
        ocr_layout.addRow("OCR Language:", self.language_combo)
        
        self.preprocessing_checkbox = QCheckBox("Включить предобработку изображений")
        self.preprocessing_checkbox.setChecked(self.settings.get('preprocessing', True))
        ocr_layout.addRow(self.preprocessing_checkbox)
        
        # Настройки качества изображения
        quality_group = QGroupBox("Настройки качества OCR")
        quality_layout = QFormLayout()
        
        self.scale_factor_spin = QSpinBox()
        self.scale_factor_spin.setRange(1, 5)
        self.scale_factor_spin.setValue(self.settings.get('scale_factor', 3))
        self.scale_factor_spin.setToolTip("Увеличение изображения для лучшего распознавания (1-5x)")
        quality_layout.addRow("Увеличение изображения:", self.scale_factor_spin)
        
        self.debug_images_checkbox = QCheckBox("Сохранять отладочные изображения")
        self.debug_images_checkbox.setChecked(self.settings.get('debug_images', False))
        self.debug_images_checkbox.setToolTip("Сохранять оригинальные и обработанные изображения в папку debug_images/")
        quality_layout.addRow(self.debug_images_checkbox)
        
        self.high_quality_checkbox = QCheckBox("Режим высокого качества (медленнее)")
        self.high_quality_checkbox.setChecked(self.settings.get('high_quality_mode', False))
        self.high_quality_checkbox.setToolTip("Использовать дополнительные алгоритмы для лучшего качества")
        quality_layout.addRow(self.high_quality_checkbox)
        
        quality_group.setLayout(quality_layout)
        ocr_layout.addRow(quality_group)
        
        self.interview_mode_checkbox = QCheckBox("Режим помощника на собеседовании")
        self.interview_mode_checkbox.setChecked(self.settings.get('interview_mode', False))
        ocr_layout.addRow(self.interview_mode_checkbox)
        
        ocr_group.setLayout(ocr_layout)
        layout.addRow(ocr_group)
        
        # Аудио настройки
        audio_group = QGroupBox("Аудио Настройки")
        audio_layout = QFormLayout()
        
        self.user_name_input = QLineEdit()
        self.user_name_input.setText(self.settings.get('user_name', ''))
        audio_layout.addRow("Ваше имя:", self.user_name_input)
        
        self.whisper_language_combo = QComboBox()
        whisper_langs = ['auto', 'ru', 'en', 'de', 'fr', 'es', 'it', 'zh']
        self.whisper_language_combo.addItems(whisper_langs)
        self.whisper_language_combo.setCurrentText(self.settings.get('whisper_language', 'auto'))
        audio_layout.addRow("Whisper Language:", self.whisper_language_combo)
        
        audio_layout.addRow(QLabel("Промпт для обработки аудио:"))
        self.audio_prompt_edit = QTextEdit()
        self.audio_prompt_edit.setMaximumHeight(100)
        default_prompt = "Переведи текст на русский язык (если нужно), исправь ошибки транскрипции, сделай текст более читаемым и выдели ключевые моменты."
        self.audio_prompt_edit.setText(self.settings.get('audio_prompt', default_prompt))
        audio_layout.addRow(self.audio_prompt_edit)
        
        # Языки для быстрых ответов
        self.response_langs_group = QGroupBox("Языки для быстрых ответов")
        response_layout = QVBoxLayout()
        
        self.ru_response_checkbox = QCheckBox("Русский")
        self.ru_response_checkbox.setChecked(self.settings.get('enable_ru_responses', True))
        response_layout.addWidget(self.ru_response_checkbox)
        
        self.en_response_checkbox = QCheckBox("English")
        self.en_response_checkbox.setChecked(self.settings.get('enable_en_responses', True))
        response_layout.addWidget(self.en_response_checkbox)
        
        self.response_langs_group.setLayout(response_layout)
        audio_layout.addRow(self.response_langs_group)
        
        audio_group.setLayout(audio_layout)
        layout.addRow(audio_group)
        
        # Настройки интерфейса
        ui_group = QGroupBox("Настройки интерфейса")
        ui_layout = QFormLayout()
        
        self.floating_windows_checkbox = QCheckBox("Отдельные плавающие окна")
        self.floating_windows_checkbox.setChecked(self.settings.get('floating_windows', True))
        ui_layout.addRow(self.floating_windows_checkbox)
        
        self.autosave_checkbox = QCheckBox("Автосохранение истории")
        self.autosave_checkbox.setChecked(self.settings.get('autosave_enabled', True))
        ui_layout.addRow(self.autosave_checkbox)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.log_level_combo.setCurrentText(self.settings.get('log_level', 'INFO'))
        ui_layout.addRow("Уровень логирования:", self.log_level_combo)
        
        ui_group.setLayout(ui_layout)
        layout.addRow(ui_group)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
    def test_api_connection(self):
        """Тестирует подключение к OpenAI API"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Ошибка", "Введите API ключ")
            return
            
        if not api_key.startswith('sk-'):
            QMessageBox.warning(self, "Ошибка", "API ключ должен начинаться с 'sk-'")
            return
            
        try:
            client = OpenAI(api_key=api_key)
            models = client.models.list()
            QMessageBox.information(self, "Успех", "✅ API ключ работает корректно!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"❌ Ошибка подключения к API:\n{str(e)}")
        
    def get_settings(self):
        return {
            'api_key': self.api_key_input.text(),
            'use_openai': self.use_openai_checkbox.isChecked(),
            'model': self.model_combo.currentText(),
            'ocr_language': self.language_combo.currentText(),
            'preprocessing': self.preprocessing_checkbox.isChecked(),
            'scale_factor': self.scale_factor_spin.value(),
            'debug_images': self.debug_images_checkbox.isChecked(),
            'high_quality_mode': self.high_quality_checkbox.isChecked(),
            'interview_mode': self.interview_mode_checkbox.isChecked(),
            'user_name': self.user_name_input.text(),
            'whisper_language': self.whisper_language_combo.currentText(),
            'audio_prompt': self.audio_prompt_edit.toPlainText(),
            'enable_ru_responses': self.ru_response_checkbox.isChecked(),
            'enable_en_responses': self.en_response_checkbox.isChecked(),
            'floating_windows': self.floating_windows_checkbox.isChecked(),
            'autosave_enabled': self.autosave_checkbox.isChecked(),
            'log_level': self.log_level_combo.currentText()
        }


class VideoWidget(QLabel):
    selectionMade = pyqtSignal(QRectF)
    
    def __init__(self):
        super().__init__()
        self.setScaledContents(False)
        self.setMouseTracking(True)
        
        self.zoom_factor = 1.0
        self.pan_offset = QPointF(0, 0)
        self.is_panning = False
        self.last_mouse_pos = QPointF()
        
        self.is_selecting = False
        self.selection_start = QPointF()
        self.selection_end = QPointF()
        self.selection_rect = QRectF()
        
        self.video_size = None
        self.widget_size = None
        
        # Показывать подсказки
        self.setToolTip("Левая кнопка: выделение области для OCR\nПравая кнопка: панорамирование\nКолесико: зум")
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: #ecf0f1;
            }
        """)
        
    def set_frame(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        
        self.video_size = q_image.size()
        self.widget_size = self.size()
        
        pixmap = QPixmap.fromImage(q_image)
        
        scaled_width = int(width * self.zoom_factor)
        scaled_height = int(height * self.zoom_factor)
        scaled_pixmap = pixmap.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        final_pixmap = QPixmap(self.size())
        final_pixmap.fill(Qt.black)
        
        painter = QPainter(final_pixmap)
        x = int((self.width() - scaled_width) / 2 + self.pan_offset.x())
        y = int((self.height() - scaled_height) / 2 + self.pan_offset.y())
        painter.drawPixmap(x, y, scaled_pixmap)
        
        if not self.selection_rect.isEmpty():
            painter.setPen(QPen(QColor(0, 255, 0), 3))
            painter.drawRect(self.selection_rect.toRect())
        
        painter.end()
        
        self.setPixmap(final_pixmap)
        
    def wheelEvent(self, event):
        old_zoom = self.zoom_factor
        
        if event.angleDelta().y() > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
            
        self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))
        
        mouse_pos = event.pos()
        zoom_change = self.zoom_factor / old_zoom
        
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        offset_x = mouse_pos.x() - center_x - self.pan_offset.x()
        offset_y = mouse_pos.y() - center_y - self.pan_offset.y()
        
        self.pan_offset.setX(self.pan_offset.x() + offset_x * (1 - zoom_change))
        self.pan_offset.setY(self.pan_offset.y() + offset_y * (1 - zoom_change))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.is_panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        elif event.button() == Qt.LeftButton:
            self.is_selecting = True
            self.selection_start = event.pos()
            self.selection_end = event.pos()
            self.selection_rect = QRectF()
            
    def mouseMoveEvent(self, event):
        if self.is_panning:
            delta = event.pos() - self.last_mouse_pos
            self.pan_offset += delta
            self.last_mouse_pos = event.pos()
        elif self.is_selecting:
            self.selection_end = event.pos()
            self.selection_rect = QRectF(self.selection_start, self.selection_end).normalized()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
        elif event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            if not self.selection_rect.isEmpty():
                self.selectionMade.emit(self.selection_rect)
                
    def get_video_coords_from_widget(self, widget_point):
        if not self.video_size or not self.widget_size:
            return None
            
        scaled_width = self.video_size.width() * self.zoom_factor
        scaled_height = self.video_size.height() * self.zoom_factor
        
        x_offset = (self.width() - scaled_width) / 2 + self.pan_offset.x()
        y_offset = (self.height() - scaled_height) / 2 + self.pan_offset.y()
        
        video_x = (widget_point.x() - x_offset) / self.zoom_factor
        video_y = (widget_point.y() - y_offset) / self.zoom_factor
        
        return QPointF(video_x, video_y)


class OBSCompleteAssistantOptimized(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OBS Complete Assistant - Optimized Version with Floating Windows")
        self.setGeometry(100, 100, 1400, 800)
        
        # Инициализация логирования
        self.setup_logging()
        
        # Видео переменные
        self.cap = None
        self.current_frame = None
        self.ocr_worker = None
        self.history = []
        self.audio_history = []
        
        # Аудио переменные
        self.audio_worker = None
        self.transcription_worker = None
        self.response_worker = None
        self.is_recording = False
        
        # Системные переменные
        self.settings = self.load_settings()
        self.session_start_time = datetime.now()
        self.last_autosave = datetime.now()
        
        # Переменные для оптимизации производительности
        self.last_ocr_hash = None
        self.performance_mode = False
        
        # Плавающие окна
        self.response_window = None
        self.audio_window = None
        
        self.setup_ui()
        self.setup_floating_windows()
        self.setup_video_capture()
        self.setup_shortcuts()
        self.setup_timers()
        
        # Проверяем доступность аудио устройств
        self.check_audio_devices()
        
        # Загружаем сохраненную историю
        self.load_history_from_file()
        
        self.logger.info("Application started successfully")
        
    def setup_logging(self):
        """Настройка системы логирования"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"obs_assistant_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_floating_windows(self):
        """Настройка плавающих окон"""
        if self.settings.get('floating_windows', True):
            # Создаем плавающее окно для быстрых ответов
            self.response_window = FloatingResponseWindow(self)
            self.response_window.generate_responses_requested.connect(self.generate_quick_responses_from_window)
            
            # Создаем плавающее окно для аудио
            self.audio_window = FloatingAudioWindow(self)
            self.audio_window.toggle_recording_requested.connect(self.toggle_recording)
            self.audio_window.save_audio_text_requested.connect(self.save_audio_text)
            
    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        # Ctrl+R - переключить запись
        self.record_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.record_shortcut.activated.connect(self.toggle_recording)
        
        # Ctrl+S - сохранить все данные
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_all_data)
        
        # Escape - отменить текущую операцию
        self.cancel_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.cancel_shortcut.activated.connect(self.cancel_current_operation)
        
        # F1 - помощь
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.show_help)
        
        # Ctrl+E - экспорт данных
        self.export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        self.export_shortcut.activated.connect(self.export_session_data)
        
        # Ctrl+1, Ctrl+2 - показать плавающие окна
        self.show_response_shortcut = QShortcut(QKeySequence("Ctrl+1"), self)
        self.show_response_shortcut.activated.connect(self.show_response_window)
        
        self.show_audio_shortcut = QShortcut(QKeySequence("Ctrl+2"), self)
        self.show_audio_shortcut.activated.connect(self.show_audio_window)
        
    def setup_timers(self):
        """Настройка таймеров"""
        # Таймер обновления видео с адаптивной частотой
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_frame)
        self.video_timer.start(33)  # 30 FPS по умолчанию
        
        # Таймер автосохранения
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave_data)
        self.autosave_timer.start(30000)  # 30 секунд
        
        # Таймер оптимизации производительности
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.optimize_performance)
        self.perf_timer.start(5000)  # 5 секунд
        
    def load_settings(self):
        load_dotenv()
        settings = {
            'api_key': os.getenv('OPENAI_API_KEY', ''),
            'use_openai': False,
            'model': 'gpt-4o',
            'ocr_language': 'eng',
            'preprocessing': True,
            'scale_factor': 3,
            'debug_images': False,
            'high_quality_mode': False,
            'interview_mode': False,
            'user_name': '',
            'whisper_language': 'auto',
            'audio_prompt': 'Переведи текст на русский язык (если нужно), исправь ошибки транскрипции, сделай текст более читаемым и выдели ключевые моменты.',
            'enable_ru_responses': True,
            'enable_en_responses': True,
            'floating_windows': True,
            'autosave_enabled': True,
            'log_level': 'INFO'
        }
        
        settings_file = 'complete_settings_optimized.json'
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    settings.update(saved_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
                
        return settings
        
    def save_settings(self):
        settings_file = 'complete_settings_optimized.json'
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
    
    def check_audio_devices(self):
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            if not input_devices:
                self.status_widget.show_message("⚠️ No audio input devices found", 5)
                self.logger.warning("No audio input devices found")
            else:
                self.status_widget.show_message(f"✅ Found {len(input_devices)} audio input device(s)", 3)
                self.logger.info(f"Found {len(input_devices)} audio input devices")
        except Exception as e:
            self.status_widget.show_message(f"⚠️ Audio check failed: {str(e)}", 5)
            self.logger.error(f"Audio check failed: {e}")
            
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем меню
        self.create_menu_bar()
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Панель управления
        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)
        
        # Видео кнопки
        self.copy_button = QPushButton("📋 Copy OCR (Ctrl+C)")
        self.copy_button.clicked.connect(self.copy_ocr_text)
        self.copy_button.setEnabled(False)
        self.copy_button.setToolTip("Копировать распознанный текст в буфер обмена")
        self.copy_button.setStyleSheet("QPushButton { background-color: #3498db; color: white; }")
        controls_layout.addWidget(self.copy_button)
        
        self.reset_view_button = QPushButton("🔄 Reset View")
        self.reset_view_button.clicked.connect(self.reset_view)
        self.reset_view_button.setToolTip("Сбросить зум и панорамирование видео")
        controls_layout.addWidget(self.reset_view_button)
        
        # Аудио кнопки
        self.record_button = QPushButton("🎤 Start Recording (Ctrl+R)")
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setStyleSheet("QPushButton { font-size: 14px; padding: 10px; background-color: #27ae60; color: white; }")
        self.record_button.setToolTip("Начать/остановить запись аудио")
        controls_layout.addWidget(self.record_button)
        
        # Кнопки плавающих окон
        self.show_response_btn = QPushButton("💬 Responses (Ctrl+1)")
        self.show_response_btn.clicked.connect(self.show_response_window)
        self.show_response_btn.setToolTip("Показать окно быстрых ответов")
        self.show_response_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; }")
        controls_layout.addWidget(self.show_response_btn)
        
        self.show_audio_btn = QPushButton("🎤 Audio (Ctrl+2)")
        self.show_audio_btn.clicked.connect(self.show_audio_window)
        self.show_audio_btn.setToolTip("Показать окно аудио транскрипции")
        self.show_audio_btn.setStyleSheet("QPushButton { background-color: #9b59b6; color: white; }")
        controls_layout.addWidget(self.show_audio_btn)
        
        # Кнопка отмены
        self.cancel_button = QPushButton("❌ Cancel (Esc)")
        self.cancel_button.clicked.connect(self.cancel_current_operation)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setToolTip("Отменить текущую операцию")
        self.cancel_button.setStyleSheet("QPushButton { background-color: #e67e22; color: white; }")
        controls_layout.addWidget(self.cancel_button)
        
        # Общие кнопки
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setToolTip("Открыть настройки приложения")
        controls_layout.addWidget(self.settings_button)
        
        controls_layout.addStretch()
        
        self.clear_button = QPushButton("🗑️ Clear All")
        self.clear_button.clicked.connect(self.clear_all_text)
        self.clear_button.setToolTip("Очистить весь текст и историю")
        self.clear_button.setStyleSheet("QPushButton { background-color: #95a5a6; color: white; }")
        controls_layout.addWidget(self.clear_button)
        
        # Статус виджет
        self.status_widget = StatusWidget()
        main_layout.addWidget(self.status_widget)
        
        # Основной контент - горизонтальный сплиттер
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Левая часть - видео
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        video_label = QLabel("📹 OBS Virtual Camera")
        video_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px; padding: 5px;")
        left_layout.addWidget(video_label)
        
        self.video_widget = VideoWidget()
        self.video_widget.selectionMade.connect(self.handle_selection)
        self.video_widget.setMinimumSize(640, 480)
        left_layout.addWidget(self.video_widget)
        
        main_splitter.addWidget(left_panel)
        
        # Правая часть - OCR редактор
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        ocr_label = QLabel("📝 OCR Text Editor")
        ocr_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px; padding: 5px;")
        right_layout.addWidget(ocr_label)
        
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 11))
        self.text_edit.setPlaceholderText("Распознанный текст с GPT-4o ответами появится здесь...")
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.text_edit)
        
        # Кнопки управления OCR текстом
        text_buttons_layout = QHBoxLayout()
        right_layout.addLayout(text_buttons_layout)
        
        self.copy_text_button = QPushButton("📋 Copy Text")
        self.copy_text_button.clicked.connect(self.copy_text_from_editor)
        self.copy_text_button.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; }")
        text_buttons_layout.addWidget(self.copy_text_button)
        
        self.save_text_button = QPushButton("💾 Save OCR")
        self.save_text_button.clicked.connect(self.save_ocr_text)
        text_buttons_layout.addWidget(self.save_text_button)
        
        self.clear_text_button = QPushButton("🗑️ Clear")
        self.clear_text_button.clicked.connect(self.text_edit.clear)
        text_buttons_layout.addWidget(self.clear_text_button)
        
        text_buttons_layout.addStretch()
        
        main_splitter.addWidget(right_panel)
        
        # История в нижней части
        history_widget = QWidget()
        history_layout = QVBoxLayout()
        history_widget.setLayout(history_layout)
        
        history_label = QLabel("📚 Session History")
        history_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px; padding: 3px;")
        history_layout.addWidget(history_label)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_history_item)
        self.history_list.setMaximumHeight(120)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
        """)
        history_layout.addWidget(self.history_list)
        
        history_buttons = QHBoxLayout()
        export_history_button = QPushButton("📤 Export")
        export_history_button.clicked.connect(self.export_history)
        history_buttons.addWidget(export_history_button)
        
        clear_history_button = QPushButton("🗑️ Clear History")
        clear_history_button.clicked.connect(self.clear_history)
        history_buttons.addWidget(clear_history_button)
        
        history_buttons.addStretch()
        history_layout.addLayout(history_buttons)
        
        main_layout.addWidget(history_widget)
        
        main_splitter.setSizes([800, 600])
        
    def create_menu_bar(self):
        """Создание меню приложения"""
        menubar = self.menuBar()
        
        # Файл меню
        file_menu = menubar.addMenu('Файл')
        
        save_action = QAction('💾 Сохранить все (Ctrl+S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_all_data)
        file_menu.addAction(save_action)
        
        export_action = QAction('📤 Экспорт сессии (Ctrl+E)', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_session_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('❌ Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Окна меню
        windows_menu = menubar.addMenu('Окна')
        
        show_response_action = QAction('💬 Быстрые ответы (Ctrl+1)', self)
        show_response_action.setShortcut('Ctrl+1')
        show_response_action.triggered.connect(self.show_response_window)
        windows_menu.addAction(show_response_action)
        
        show_audio_action = QAction('🎤 Аудио транскрипция (Ctrl+2)', self)
        show_audio_action.setShortcut('Ctrl+2')
        show_audio_action.triggered.connect(self.show_audio_window)
        windows_menu.addAction(show_audio_action)
        
        windows_menu.addSeparator()
        
        organize_windows_action = QAction('📐 Упорядочить окна', self)
        organize_windows_action.triggered.connect(self.organize_windows)
        windows_menu.addAction(organize_windows_action)
        
        # Инструменты меню
        tools_menu = menubar.addMenu('Инструменты')
        
        record_action = QAction('🎤 Запись аудио (Ctrl+R)', self)
        record_action.setShortcut('Ctrl+R')
        record_action.triggered.connect(self.toggle_recording)
        tools_menu.addAction(record_action)
        
        cancel_action = QAction('❌ Отменить операцию (Esc)', self)
        cancel_action.setShortcut('Esc')
        cancel_action.triggered.connect(self.cancel_current_operation)
        tools_menu.addAction(cancel_action)
        
        tools_menu.addSeparator()
        
        settings_action = QAction('⚙️ Настройки', self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        # Помощь меню
        help_menu = menubar.addMenu('Помощь')
        
        help_action = QAction('❓ Справка (F1)', self)
        help_action.setShortcut('F1')
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction('ℹ️ О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def show_response_window(self):
        """Показать окно быстрых ответов"""
        if self.response_window:
            self.response_window.show()
            self.response_window.raise_()
            self.response_window.activateWindow()
            self.status_widget.show_message("Response window opened", 2)
            
    def show_audio_window(self):
        """Показать окно аудио транскрипции"""
        if self.audio_window:
            self.audio_window.show()
            self.audio_window.raise_()
            self.audio_window.activateWindow()
            self.status_widget.show_message("Audio window opened", 2)
            
    def organize_windows(self):
        """Упорядочить окна"""
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        
        # Главное окно слева
        self.setGeometry(50, 50, 1000, 700)
        
        # Окно ответов справа сверху
        if self.response_window:
            self.response_window.setGeometry(screen_rect.width() - 500, 50, 450, 400)
            self.response_window.show()
            
        # Окно аудио справа снизу
        if self.audio_window:
            self.audio_window.setGeometry(screen_rect.width() - 500, 470, 450, 400)
            self.audio_window.show()
            
        self.status_widget.show_message("Windows organized", 2)
        
    def setup_video_capture(self):
        for i in range(10):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    
                    backend = cap.getBackendName()
                    if "DSHOW" in backend or "DirectShow" in backend:
                        self.cap = cap
                        self.status_widget.show_message(f"Connected to camera {i}", 3)
                        self.logger.info(f"Connected to camera {i}")
                        break
                cap.release()
                
        if not self.cap:
            self.status_widget.show_message("No DirectShow camera found - Audio recording available", 5)
            self.logger.warning("No DirectShow camera found")
            
    def optimize_performance(self):
        """Динамическая оптимизация производительности"""
        # Если нет активных операций, снижаем частоту обновления видео
        active_operations = any([
            self.ocr_worker and self.ocr_worker.isRunning(),
            self.transcription_worker and self.transcription_worker.isRunning(),
            self.response_worker and self.response_worker.isRunning(),
            self.video_widget.is_selecting,
            self.video_widget.is_panning
        ])
        
        if not active_operations and not self.performance_mode:
            self.video_timer.setInterval(100)  # 10 FPS
            self.performance_mode = True
            self.logger.debug("Switched to performance mode (10 FPS)")
        elif active_operations and self.performance_mode:
            self.video_timer.setInterval(33)   # 30 FPS
            self.performance_mode = False
            self.logger.debug("Switched to normal mode (30 FPS)")
            
    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.video_widget.set_frame(frame)
                
    def handle_selection(self, rect):
        self.selected_rect = rect
        self.copy_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.status_widget.show_progress("Processing OCR with GPT-4o...", 0)
        self.process_ocr()
        
    def preprocess_image(self, image):
        """Улучшенная предобработка изображения для лучшего OCR"""
        # Увеличиваем изображение в соответствии с настройками
        scale_factor = self.settings.get('scale_factor', 3)
        high_quality = self.settings.get('high_quality_mode', False)
        height, width = image.shape[:2] if len(image.shape) == 3 else image.shape
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Используем INTER_CUBIC для лучшего качества при увеличении
        upscaled = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Конвертируем в оттенки серого
        if len(upscaled.shape) == 3:
            gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
        else:
            gray = upscaled
        
        # Применяем Gaussian blur для сглаживания шума
        if high_quality:
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        else:
            blurred = cv2.GaussianBlur(gray, (1, 1), 0)
        
        # Улучшенная денойзинг обработка
        if high_quality:
            # Более сильная денойзинг обработка для высокого качества
            denoised = cv2.fastNlMeansDenoising(blurred, h=8, templateWindowSize=9, searchWindowSize=23)
        else:
            denoised = cv2.fastNlMeansDenoising(blurred, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Улучшение контраста с помощью CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Адаптивная бинаризация для лучшего результата на разных типах текста
        adaptive_thresh = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Также пробуем OTSU метод
        _, otsu_thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Выбираем лучший результат на основе количества белых пикселей
        adaptive_white = np.sum(adaptive_thresh == 255)
        otsu_white = np.sum(otsu_thresh == 255)
        
        # Используем тот метод, который дает больше белых пикселей (обычно лучше для текста)
        if adaptive_white > otsu_white:
            binary = adaptive_thresh
        else:
            binary = otsu_thresh
        
        # Морфологические операции для очистки
        if high_quality:
            # Более тщательная обработка для высокого качества
            kernel_small = np.ones((1, 1), np.uint8)
            kernel_medium = np.ones((2, 2), np.uint8)
            kernel_large = np.ones((3, 3), np.uint8)
            
            # Удаляем очень мелкий шум
            opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small, iterations=1)
            
            # Заполняем пробелы в буквах
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel_medium, iterations=2)
            
            # Дополнительная очистка
            processed = cv2.morphologyEx(closing, cv2.MORPH_GRADIENT, kernel_large, iterations=1)
            processed = cv2.bitwise_or(closing, processed)
            
            # Финальная очистка
            processed = cv2.medianBlur(processed, 5)
        else:
            # Стандартная обработка
            kernel = np.ones((2, 2), np.uint8)
            
            # Удаляем мелкий шум
            opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Заполняем пробелы в буквах
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # Дополнительная очистка от мелких артефактов
            processed = cv2.medianBlur(closing, 3)
        
        return processed
        
    def process_ocr(self):
        if self.current_frame is None or not hasattr(self, 'selected_rect'):
            return
            
        top_left = self.video_widget.get_video_coords_from_widget(self.selected_rect.topLeft())
        bottom_right = self.video_widget.get_video_coords_from_widget(self.selected_rect.bottomRight())
        
        if not top_left or not bottom_right:
            return
            
        x1 = max(0, int(top_left.x()))
        y1 = max(0, int(top_left.y()))
        x2 = min(self.current_frame.shape[1], int(bottom_right.x()))
        y2 = min(self.current_frame.shape[0], int(bottom_right.y()))
        
        if x2 <= x1 or y2 <= y1:
            self.status_widget.show_message("Invalid selection", 3)
            return
            
        roi = self.current_frame[y1:y2, x1:x2]
        
        # Проверяем минимальный размер выделенной области
        if roi.shape[0] < 20 or roi.shape[1] < 20:
            self.status_widget.show_message("Selection too small for OCR", 3)
            return
        
        # Проверка кеша для избежания повторной обработки
        roi_hash = hash(roi.tobytes())
        if roi_hash == self.last_ocr_hash:
            self.status_widget.show_message("Using cached OCR result", 2)
            return
        self.last_ocr_hash = roi_hash
        
        if self.settings.get('preprocessing', True):
            processed_roi = self.preprocess_image(roi)
            pil_image = Image.fromarray(processed_roi)
            
            # Опционально сохраняем отладочные изображения
            if self.settings.get('debug_images', False):
                try:
                    debug_dir = "debug_images"
                    os.makedirs(debug_dir, exist_ok=True)
                    
                    # Сохраняем оригинал и обработанное изображение
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f"{debug_dir}/original_{timestamp}.png", roi)
                    cv2.imwrite(f"{debug_dir}/processed_{timestamp}.png", processed_roi)
                    print(f"Debug images saved to {debug_dir}/")
                except Exception as e:
                    print(f"Failed to save debug images: {e}")
        else:
            # Даже без preprocessing применяем минимальные улучшения
            if len(roi.shape) == 3:
                rgb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            else:
                rgb_roi = roi
                
            # Увеличиваем изображение хотя бы в 2 раза
            height, width = rgb_roi.shape[:2]
            upscaled = cv2.resize(rgb_roi, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
            pil_image = Image.fromarray(upscaled)
            
        if self.settings.get('ocr_language', 'eng') != 'eng':
            pytesseract.pytesseract.tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
            os.environ['TESSDATA_PREFIX'] = os.path.dirname(pytesseract.pytesseract.tesseract_cmd)
            
        # Показываем информацию о качестве обработки
        quality_info = []
        if self.settings.get('preprocessing', True):
            scale = self.settings.get('scale_factor', 3)
            quality_info.append(f"Scale: {scale}x")
            if self.settings.get('high_quality_mode', False):
                quality_info.append("HQ mode")
        
        status_msg = f"Processing OCR ({', '.join(quality_info) if quality_info else 'Standard'})..."
        self.status_widget.show_message(status_msg, 2)
        
        self.ocr_worker = OCRWorker(
            pil_image, 
            self.settings.get('use_openai', False),
            self.settings.get('api_key', ''),
            self.settings.get('model', 'gpt-4o'),
            self.settings.get('interview_mode', False)
        )
        self.ocr_worker.result_ready.connect(self.handle_ocr_result)
        self.ocr_worker.error_occurred.connect(self.handle_ocr_error)
        self.ocr_worker.progress_updated.connect(self.handle_ocr_progress)
        self.ocr_worker.start()
        
        self.logger.info("Started OCR processing with GPT-4o")
        
    @pyqtSlot(int)
    def handle_ocr_progress(self, progress):
        self.status_widget.show_progress(f"Processing OCR with GPT-4o... {progress}%", progress)
        
    @pyqtSlot(str, str, str)
    def handle_ocr_result(self, raw_text, processed_text, content_type):
        self.cancel_button.setEnabled(False)
        self.status_widget.hide_progress()
        
        if processed_text:
            # Форматируем результат с указанием что это GPT-4o ответ
            display_text = f"🤖 GPT-4o Response [{content_type.upper()}]\n"
            display_text += "=" * 50 + "\n\n"
            
            if content_type != "text":
                display_text += f"📝 Original OCR Text:\n{raw_text}\n\n"
                display_text += "🔄 " + "=" * 45 + "\n\n"
            
            display_text += f"✨ GPT-4o Analysis:\n{processed_text}"
            
            self.text_edit.setText(display_text)
            self.add_to_history(display_text, content_type)
            
            type_labels = {
                "question": "Вопрос", "task": "Задача", "text": "Текст",
                "algorithm": "Алгоритм", "code_review": "Код-ревью", 
                "logic_puzzle": "Логика", "programming_task": "Программирование"
            }
            self.status_widget.show_message(f"✅ GPT-4o: {type_labels.get(content_type, 'Текст')} обработан ({len(processed_text)} символов)", 5)
            self.logger.info(f"OCR completed with GPT-4o: {content_type}, {len(processed_text)} characters")
        else:
            self.status_widget.show_message("OCR: Текст не обнаружен", 3)
            self.logger.warning("OCR: No text detected")
            
    @pyqtSlot(str)
    def handle_ocr_error(self, error_msg):
        self.cancel_button.setEnabled(False)
        self.status_widget.hide_progress()
        self.status_widget.show_message(f"OCR Error: {error_msg}", 10)
        self.logger.error(f"OCR Error: {error_msg}")
        self.show_error_dialog("OCR Error", error_msg)
        
    def add_to_history(self, text, content_type="text"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        preview = text[:80] + "..." if len(text) > 80 else text
        type_emoji = {
            "question": "❓", "task": "📝", "text": "📄",
            "algorithm": "⚙️", "code_review": "🔍", 
            "logic_puzzle": "🧩", "programming_task": "💻"
        }
        item_text = f"[{timestamp}] {type_emoji.get(content_type, '📄')} {preview}"
        
        self.history.append({
            'timestamp': timestamp,
            'text': text,
            'preview': preview,
            'type': content_type
        })
        
        self.history_list.insertItem(0, item_text)
        
        if self.history_list.count() > 100:
            self.history_list.takeItem(100)
            self.history.pop()
            
    def load_history_item(self, item):
        index = self.history_list.row(item)
        if 0 <= index < len(self.history):
            self.text_edit.setText(self.history[index]['text'])
            
    def clear_history(self):
        reply = QMessageBox.question(self, 'Подтверждение', 
                                   'Вы уверены, что хотите очистить всю историю?',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history.clear()
            self.history_list.clear()
            self.audio_history.clear()
            self.status_widget.show_message("История очищена", 3)
            self.logger.info("History cleared")
            
    def copy_ocr_text(self):
        text = self.text_edit.toPlainText()
        if text:
            pyperclip.copy(text)
            self.status_widget.show_message("GPT-4o OCR result copied to clipboard", 2)
            self.logger.info("OCR text copied to clipboard")
            
    def copy_text_from_editor(self):
        text = self.text_edit.toPlainText()
        if text:
            pyperclip.copy(text)
            self.status_widget.show_message("Text copied to clipboard", 2)
            self.logger.info("Text copied to clipboard")
            
    def reset_view(self):
        self.video_widget.zoom_factor = 1.0
        self.video_widget.pan_offset = QPointF(0, 0)
        self.video_widget.selection_rect = QRectF()
        self.copy_button.setEnabled(False)
        self.status_widget.show_message("View reset", 2)
        self.logger.info("View reset")
        
    # Аудио методы
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        if not self.settings.get('api_key'):
            self.show_error_dialog("Configuration Error", "Please configure OpenAI API key in Settings")
            return
            
        try:
            self.audio_worker = AudioCaptureWorker()
            self.audio_worker.audio_captured.connect(self.handle_audio_data)
            self.audio_worker.error_occurred.connect(self.handle_audio_error)
            
            self.audio_worker.start_recording()
            self.is_recording = True
            
            self.record_button.setText("⏹️ Stop Recording (Ctrl+R)")
            self.record_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-size: 14px; padding: 10px; }")
            self.status_widget.show_message("🔴 Recording audio...")
            
            # Обновляем состояние в аудио окне
            if self.audio_window:
                self.audio_window.set_recording_state(True)
                
            self.logger.info("Audio recording started")
            
        except Exception as e:
            self.status_widget.show_message(f"Audio Error: {str(e)}", 10)
            self.logger.error(f"Audio recording error: {e}")
            self.show_error_dialog("Audio Error", str(e))
            
    def stop_recording(self):
        if self.audio_worker:
            self.audio_worker.stop_recording()
            self.audio_worker.wait(5000)  # Ждем максимум 5 секунд
            if self.audio_worker.isRunning():
                self.audio_worker.terminate()
            self.audio_worker = None
            
        self.is_recording = False
        self.record_button.setText("🎤 Start Recording (Ctrl+R)")
        self.record_button.setStyleSheet("QPushButton { font-size: 14px; padding: 10px; background-color: #27ae60; color: white; }")
        self.status_widget.show_message("Ready", 2)
        
        # Обновляем состояние в аудио окне
        if self.audio_window:
            self.audio_window.set_recording_state(False)
            
        self.logger.info("Audio recording stopped")
        
    @pyqtSlot(bytes)
    def handle_audio_data(self, audio_data):
        # Запускаем транскрипцию в отдельном потоке
        self.transcription_worker = TranscriptionWorker(
            audio_data, 
            self.settings, 
            self.settings.get('user_name', '')
        )
        self.transcription_worker.transcription_ready.connect(self.handle_transcription)
        self.transcription_worker.error_occurred.connect(self.handle_transcription_error)
        self.transcription_worker.progress_updated.connect(self.handle_transcription_progress)
        self.transcription_worker.start()
        
        self.status_widget.show_progress("Processing audio...", 0)
        self.cancel_button.setEnabled(True)
        
        # Обновляем статус в аудио окне
        if self.audio_window:
            self.audio_window.set_status("🔄 Processing audio...")
        
    @pyqtSlot(int)
    def handle_transcription_progress(self, progress):
        self.status_widget.show_progress(f"Processing audio... {progress}%", progress)
        
    @pyqtSlot(str, str)
    def handle_transcription(self, original_text, processed_text):
        self.cancel_button.setEnabled(False)
        self.status_widget.hide_progress()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Добавляем в аудио окно
        if self.audio_window:
            self.audio_window.add_transcription(f"[{timestamp}] {original_text}")
            self.audio_window.add_processed_text(f"[{timestamp}] {processed_text}")
        
        # Добавляем в аудио историю
        self.audio_history.append({
            'timestamp': timestamp,
            'original': original_text,
            'processed': processed_text
        })
        
        # Проверяем, упоминается ли имя пользователя
        user_name = self.settings.get('user_name', '')
        if user_name and user_name.lower() in original_text.lower():
            self.status_widget.show_message(f"👤 Your name mentioned! Check Quick Responses", 5)
            
            # Автоматически открываем окно ответов и генерируем ответы
            if self.response_window:
                self.response_window.set_question(original_text)
                self.response_window.show()
                self.response_window.raise_()
                self.generate_quick_responses_from_window(original_text)
        else:
            self.status_widget.show_message("🔴 Recording audio...")
            
        # Обновляем статус в аудио окне
        if self.audio_window:
            if user_name and user_name.lower() in original_text.lower():
                self.audio_window.set_status(f"👤 Your name mentioned!")
            else:
                self.audio_window.set_status("🔴 Recording...")
            
        self.logger.info(f"Audio transcribed: {len(original_text)} characters")
            
    @pyqtSlot(str)
    def handle_transcription_error(self, error_msg):
        self.cancel_button.setEnabled(False)
        self.status_widget.hide_progress()
        self.status_widget.show_message(f"Transcription Error: {error_msg}", 10)
        
        if self.audio_window:
            self.audio_window.set_status(f"❌ Error: {error_msg}")
            
        self.logger.error(f"Transcription Error: {error_msg}")
        self.show_error_dialog("Transcription Error", error_msg)
        
    @pyqtSlot(str)
    def handle_audio_error(self, error_msg):
        self.status_widget.show_message(f"Audio Error: {error_msg}", 10)
        
        if self.audio_window:
            self.audio_window.set_status(f"❌ Audio Error: {error_msg}")
            
        self.logger.error(f"Audio Error: {error_msg}")
        self.show_error_dialog("Audio Error", error_msg)
        self.stop_recording()
        
    def generate_quick_responses_from_window(self, question):
        """Генерация ответов из плавающего окна"""
        self.generate_quick_responses(question)
        
    def generate_quick_responses(self, question=None):
        if question is None:
            question = self.response_window.question_input.text().strip() if self.response_window else ""
            
        if not question:
            return
            
        if not self.settings.get('api_key'):
            if self.response_window:
                self.response_window.set_responses("❌ OpenAI API key not configured", "❌ OpenAI API key not configured")
            return
            
        self.response_worker = QuickResponseWorker(
            question, 
            self.settings, 
            self.settings.get('user_name', '')
        )
        self.response_worker.response_ready.connect(self.handle_responses)
        self.response_worker.error_occurred.connect(self.handle_response_error)
        self.response_worker.progress_updated.connect(self.handle_response_progress)
        self.response_worker.start()
        
        if self.response_window:
            self.response_window.set_status("🔄 Generating GPT-4o responses...")
            
        self.status_widget.show_progress("Generating responses...", 0)
        self.cancel_button.setEnabled(True)
        
        self.logger.info("Started generating quick responses with GPT-4o")
        
    @pyqtSlot(int)
    def handle_response_progress(self, progress):
        self.status_widget.show_progress(f"Generating GPT-4o responses... {progress}%", progress)
        
    @pyqtSlot(str, str)
    def handle_responses(self, ru_response, en_response):
        self.cancel_button.setEnabled(False)
        self.status_widget.hide_progress()
        
        # Обновляем окно ответов
        if self.response_window:
            if self.settings.get('enable_ru_responses', True):
                final_ru = ru_response
            else:
                final_ru = "Russian responses disabled in settings"
                
            if self.settings.get('enable_en_responses', True):
                final_en = en_response
            else:
                final_en = "English responses disabled in settings"
                
            self.response_window.set_responses(final_ru, final_en)
            
        self.status_widget.show_message("✅ GPT-4o responses generated", 3)
        self.logger.info("Quick responses generated successfully with GPT-4o")
            
    @pyqtSlot(str)
    def handle_response_error(self, error_msg):
        self.cancel_button.setEnabled(False)
        self.status_widget.hide_progress()
        
        if self.response_window:
            self.response_window.set_responses(f"❌ Error: {error_msg}", f"❌ Error: {error_msg}")
            
        self.logger.error(f"Response generation error: {error_msg}")
        self.show_error_dialog("Response Generation Error", error_msg)
        
    def cancel_current_operation(self):
        """Отменить текущую операцию"""
        cancelled_something = False
        
        if self.ocr_worker and self.ocr_worker.isRunning():
            self.ocr_worker.cancel()
            self.ocr_worker.quit()
            self.ocr_worker.wait(3000)
            cancelled_something = True
            self.logger.info("OCR operation cancelled")
            
        if self.transcription_worker and self.transcription_worker.isRunning():
            self.transcription_worker.cancel()
            self.transcription_worker.quit()
            self.transcription_worker.wait(3000)
            cancelled_something = True
            self.logger.info("Transcription operation cancelled")
            
        if self.response_worker and self.response_worker.isRunning():
            self.response_worker.cancel()
            self.response_worker.quit()
            self.response_worker.wait(3000)
            cancelled_something = True
            self.logger.info("Response generation cancelled")
            
        if cancelled_something:
            self.cancel_button.setEnabled(False)
            self.status_widget.hide_progress()
            self.status_widget.show_message("Operation cancelled", 3)
        else:
            self.status_widget.show_message("No operations to cancel", 2)
            
    def cleanup_workers(self):
        """Очистка всех worker'ов"""
        workers = [self.ocr_worker, self.audio_worker, self.transcription_worker, self.response_worker]
        for worker in workers:
            if worker and worker.isRunning():
                worker.quit()
                worker.wait(5000)  # Ждать максимум 5 секунд
                if worker.isRunning():
                    worker.terminate()
                    
    def autosave_data(self):
        """Автосохранение данных"""
        if not self.settings.get('autosave_enabled', True):
            return
            
        try:
            self.save_history_to_file()
            self.save_settings()
            self.last_autosave = datetime.now()
            self.logger.debug("Autosave completed")
        except Exception as e:
            self.logger.error(f"Autosave failed: {e}")
            
    def save_all_data(self):
        """Сохранить все данные вручную"""
        try:
            self.save_history_to_file()
            self.save_settings()
            self.status_widget.show_message("All data saved successfully", 3)
            self.logger.info("Manual save completed")
        except Exception as e:
            self.status_widget.show_message(f"Save failed: {str(e)}", 5)
            self.logger.error(f"Manual save failed: {e}")
            self.show_error_dialog("Save Error", str(e))
            
    def save_history_to_file(self):
        """Сохранение истории в файл"""
        history_dir = Path("history")
        history_dir.mkdir(exist_ok=True)
        
        history_file = history_dir / f'history_{datetime.now().strftime("%Y%m%d")}.json'
        
        data = {
            'session_start': self.session_start_time.isoformat(),
            'last_save': datetime.now().isoformat(),
            'ocr_history': self.history,
            'audio_history': self.audio_history
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def load_history_from_file(self):
        """Загрузка истории из файла"""
        history_dir = Path("history")
        if not history_dir.exists():
            return
            
        history_file = history_dir / f'history_{datetime.now().strftime("%Y%m%d")}.json'
        
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.history = data.get('ocr_history', [])
                self.audio_history = data.get('audio_history', [])
                
                # Восстанавливаем списки истории
                for item in self.history:
                    timestamp = item.get('timestamp', '')
                    type_emoji = {
                        "question": "❓", "task": "📝", "text": "📄",
                        "algorithm": "⚙️", "code_review": "🔍", 
                        "logic_puzzle": "🧩", "programming_task": "💻"
                    }
                    preview = item.get('preview', '')
                    content_type = item.get('type', 'text')
                    item_text = f"[{timestamp}] {type_emoji.get(content_type, '📄')} {preview}"
                    self.history_list.addItem(item_text)
                    
                self.logger.info(f"Loaded history: {len(self.history)} OCR items, {len(self.audio_history)} audio items")
                
            except Exception as e:
                self.logger.error(f"Failed to load history: {e}")
                
    def export_session_data(self):
        """Экспорт данных сессии"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Session Data", 
                f"obs_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON files (*.json)"
            )
            
            if filename:
                data = {
                    'session_start': self.session_start_time.isoformat(),
                    'export_time': datetime.now().isoformat(),
                    'settings': self.settings,
                    'ocr_history': self.history,
                    'audio_history': self.audio_history,
                    'current_ocr_text': self.text_edit.toPlainText()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
                self.status_widget.show_message(f"Session data exported to {filename}", 5)
                self.logger.info(f"Session data exported to {filename}")
                
        except Exception as e:
            self.status_widget.show_message(f"Export failed: {str(e)}", 5)
            self.logger.error(f"Export failed: {e}")
            self.show_error_dialog("Export Error", str(e))
            
    def export_history(self):
        """Экспорт только истории"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Export History", 
                f"obs_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON files (*.json)"
            )
            
            if filename:
                data = {
                    'export_time': datetime.now().isoformat(),
                    'ocr_history': self.history,
                    'audio_history': self.audio_history
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
                self.status_widget.show_message(f"History exported to {filename}", 5)
                self.logger.info(f"History exported to {filename}")
                
        except Exception as e:
            self.show_error_dialog("Export Error", str(e))
            
    def save_ocr_text(self):
        """Сохранить текст OCR в файл"""
        text = self.text_edit.toPlainText()
        if not text:
            self.status_widget.show_message("No OCR text to save", 3)
            return
            
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Save OCR Text", 
                f"gpt4o_ocr_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text files (*.txt)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.status_widget.show_message(f"GPT-4o OCR text saved to {filename}", 3)
                
        except Exception as e:
            self.show_error_dialog("Save Error", str(e))
            
    def save_audio_text(self):
        """Сохранить аудио текст в файл"""
        if not self.audio_window:
            return
            
        text = self.audio_window.processed_area.toPlainText()
        if not text:
            self.status_widget.show_message("No audio text to save", 3)
            return
            
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Audio Text", 
                f"audio_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text files (*.txt)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.status_widget.show_message(f"Audio text saved to {filename}", 3)
                
        except Exception as e:
            self.show_error_dialog("Save Error", str(e))
            
    def show_error_dialog(self, title, message):
        """Показать диалог ошибки"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
        
    def show_help(self):
        """Показать справку"""
        help_text = """
        <h2>OBS Complete Assistant - Optimized Version</h2>
        
        <h3>🎮 Горячие клавиши:</h3>
        <ul>
        <li><b>Ctrl+C</b> - Копировать OCR текст</li>
        <li><b>Ctrl+R</b> - Начать/остановить запись аудио</li>
        <li><b>Ctrl+S</b> - Сохранить все данные</li>
        <li><b>Ctrl+E</b> - Экспорт сессии</li>
        <li><b>Ctrl+1</b> - Показать окно быстрых ответов</li>
        <li><b>Ctrl+2</b> - Показать окно аудио транскрипции</li>
        <li><b>Esc</b> - Отменить текущую операцию</li>
        <li><b>F1</b> - Показать эту справку</li>
        </ul>
        
        <h3>🪟 Плавающие окна:</h3>
        <ul>
        <li><b>Response Window</b> - Быстрые ответы с GPT-4o на двух языках</li>
        <li><b>Audio Window</b> - Транскрипция и обработка аудио в реальном времени</li>
        <li>Окна можно закрепить поверх всех остальных</li>
        <li>Окна автоматически упорядочиваются при запуске</li>
        </ul>
        
        <h3>🤖 GPT-4o интеграция:</h3>
        <ul>
        <li>Все ответы генерируются с помощью GPT-4o</li>
        <li>Специальные промпты для собеседований</li>
        <li>Автоматическое определение типа контента</li>
        <li>Детальное форматирование результатов</li>
        </ul>
        
        <h3>📹 Управление видео:</h3>
        <ul>
        <li><b>Левая кнопка мыши</b> - Выделить область для OCR</li>
        <li><b>Правая кнопка мыши + перетаскивание</b> - Панорамирование</li>
        <li><b>Колесико мыши</b> - Зум</li>
        </ul>
        """
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Справка")
        msg.setText(help_text)
        msg.setTextFormat(Qt.RichText)
        msg.exec_()
        
    def show_about(self):
        """Показать информацию о программе"""
        about_text = f"""
        <h2>OBS Complete Assistant</h2>
        <p><b>Optimized Version with Floating Windows</b></p>
        <p>Версия: 3.0</p>
        <p>Дата: {datetime.now().strftime('%Y-%m-%d')}</p>
        
        <p>Полнофункциональный помощник с:</p>
        <ul>
        <li>📹 Захват видео из OBS Virtual Camera</li>
        <li>📝 OCR с GPT-4o обработкой</li>
        <li>🎤 Захват и обработка аудио</li>
        <li>💬 Быстрые ответы на конференциях</li>
        <li>🪟 Отдельные плавающие окна</li>
        <li>🎯 Помощь на собеседованиях</li>
        </ul>
        
        <p><b>Новое в этой версии:</b></p>
        <ul>
        <li>🪟 Отдельные окна для разных функций</li>
        <li>🤖 Четкое отображение GPT-4o ответов</li>
        <li>⚡ Оптимизированный интерфейс</li>
        <li>📌 Закрепление окон поверх всех</li>
        </ul>
        
        <p>Технологии: PyQt5, OpenCV, Tesseract, OpenAI GPT-4o API</p>
        """
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("О программе")
        msg.setText(about_text)
        msg.setTextFormat(Qt.RichText)
        msg.exec_()
        
    def open_settings(self):
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec_():
            old_floating = self.settings.get('floating_windows', True)
            self.settings = dialog.get_settings()
            self.save_settings()
            self.status_widget.show_message("Settings updated", 3)
            self.logger.info("Settings updated")
            
            # Обновляем уровень логирования
            log_level = getattr(logging, self.settings.get('log_level', 'INFO'))
            logging.getLogger().setLevel(log_level)
            
            # Если изменилась настройка плавающих окон
            new_floating = self.settings.get('floating_windows', True)
            if old_floating != new_floating:
                if new_floating and not self.response_window:
                    self.setup_floating_windows()
                elif not new_floating and self.response_window:
                    self.response_window.hide()
                    self.audio_window.hide()
            
    def clear_all_text(self):
        reply = QMessageBox.question(self, 'Подтверждение', 
                                   'Очистить весь текст? Это действие нельзя отменить.',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.text_edit.clear()
            
            if self.response_window:
                self.response_window.ru_response_area.clear()
                self.response_window.en_response_area.clear()
                self.response_window.question_input.clear()
                
            if self.audio_window:
                self.audio_window.clear_all_text()
                
            self.status_widget.show_message("All text cleared", 3)
            self.logger.info("All text cleared")
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.copy_ocr_text()
            
    def closeEvent(self, event):
        # Сохранение данных перед закрытием
        self.save_all_data()
        
        # Скрываем плавающие окна
        if self.response_window:
            self.response_window.hide()
        if self.audio_window:
            self.audio_window.hide()
        
        # Очистка ресурсов
        if self.cap:
            self.cap.release()
        self.stop_recording()
        self.cleanup_workers()
        
        self.logger.info("Application closed")
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OBS Complete Assistant Optimized")
    app.setApplicationVersion("3.0")
    
    # Проверяем наличие sounddevice
    try:
        import sounddevice as sd
        print("✅ sounddevice loaded successfully")
    except ImportError:
        print("⚠️ sounddevice not installed. Audio features will be limited.")
        print("Run: pip install sounddevice")
    
    window = OBSCompleteAssistantOptimized()
    window.show()
    
    # Автоматически упорядочиваем окна при запуске
    QTimer.singleShot(1000, window.organize_windows)
    
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {e}")
        window.logger.error(f"Application error: {e}")


if __name__ == "__main__":
    main()