# OBS Complete Assistant

A comprehensive assistant program for capturing video from OBS Virtual Camera with OCR and audio assistant for conferences.

## 🚀 Key Features

### 📹 Video OCR Functions
- Capture video from OBS Virtual Camera (any DirectShow device)
- Smooth zoom with mouse wheel focused on cursor
- Panning with right-click drag
- Left-click area selection for OCR
- Intelligent image preprocessing for better OCR

### 🧠 OCR and Text Processing
- Text recognition via Tesseract OCR
- Support for multiple languages (English, Russian, German, etc.)
- OpenAI API integration for text processing and formatting
- **Special interview assistant mode** with task type detection:
  - ⚙️ Algorithmic problems with complexity analysis
  - 🔍 Code review with detailed analysis
  - 🧩 Logic puzzles and brain teasers
  - 💻 Programming tasks with code examples
- Context window for editing recognized text
- History of all recognized texts with timestamps

### 🎤 Audio Assistant for Conferences
- **Real-time audio capture** from microphone
- **Speech-to-Text** via OpenAI Whisper API
- **Smart processing** of transcription via GPT-4o
- **Automatic name detection** of user in conversation
- **Quick responses** in two languages (Russian/English) when name is mentioned
- **Customizable prompts** for audio processing
- **Audio history** with timestamps

### ⚙️ Additional Features
- Unified settings for all functions
- Settings persistence between sessions
- Multi-threaded OCR and audio processing
- One-click text copying to clipboard
- Support for various OpenAI models (GPT-4o, GPT-4, etc.)

## Installation

1. Install Python 3.8+

2. Install Tesseract OCR:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-rus`
   - macOS: `brew install tesseract tesseract-lang`

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Configure OpenAI API:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file
   - Or enter the key through the Settings menu in the program

## Usage

### Startup
1. Launch OBS and enable Virtual Camera (for video OCR)
2. Run the application:
```bash
python obs_assistant.py
```

### 🎮 Controls

#### Video OCR:
- **Mouse wheel** - smooth video zoom
- **Right-click + drag** - video panning
- **Left-click** - area selection for OCR
- **Ctrl+C** - copy text from editor
- **Reset View** - reset zoom and panning

#### Audio:
- **🎤 Start Recording** - start audio capture
- **⏹️ Stop Recording** - stop audio capture
- **Generate** - manually generate quick responses

### ⚙️ Settings
- **OpenAI API Key**: for OCR and audio processing
- **OpenAI Model**: model selection (GPT-4o, GPT-4, etc.)
- **OCR Language**: text recognition language
- **Interview Mode**: special mode for interviews
- **Whisper Language**: language for speech recognition
- **User Name**: your name for automatic detection
- **Audio Prompt**: customizable prompt for audio processing

### 📊 Interface Panels
- **📝 OCR**: editing and viewing recognized text
- **🎤 Audio**: transcription and processed audio text in real-time
- **💬 Responses**: quick responses in Russian and English
- **📚 History**: OCR and audio history with timestamps

## 📁 Project Files

- **`obs_assistant.py`** - 🚀 **MAIN APPLICATION** with all features and optimizations
- `requirements.txt` - Python dependencies
- `.env.example` - environment file example for API keys
- `complete_settings_optimized.json` - program settings file (created automatically)
- `install.py` / `install.bat` / `install.sh` - installation scripts
- `INSTALL.md` - detailed installation guide

## 💼 Use Cases

### 🎯 For Interviews:
1. Enable **Interview Mode** in settings
2. Use OCR to recognize tasks on screen
3. Get detailed solutions for algorithmic problems
4. Analyze code and get improvement suggestions

### 🏢 For Conferences:
1. Set your name in **User Name**
2. Start audio recording during meetings
3. Get translations and processed transcriptions
4. Automatically generate responses when your name is mentioned

### 📚 For Learning:
1. Use OCR to recognize text from lectures
2. Get explanations of complex concepts via AI
3. Save important information in history

## 🔧 Advanced Features

### Supported OCR Formats:
- Mathematical formulas and equations
- Program code in various languages
- Logic problems and algorithms
- Regular text in multiple languages

### Audio Functions:
- Automatic transcription with error correction
- Real-time translation between languages
- Smart processing of technical terms
- Saving history of all conversations

## 🚀 New in Improved Version

### 🎮 Extended Controls:
- **Hotkeys**: Ctrl+R (record), Ctrl+S (save), Esc (cancel), F1 (help)
- **Application menu** with quick access to all functions
- **Context tooltips** for all interface elements
- **Operation cancellation** - can interrupt any long operation

### 💾 Auto-save and Data Management:
- **Auto-save history** every 30 seconds
- **Session recovery** on restart
- **Data export** in JSON/TXT formats
- **History loading** from previous sessions
- **Settings validation** with API key checking

### 📊 Improved Interface:
- **Progress bars** for all long operations
- **Extended statuses** with detailed information
- **Error dialogs** with detailed messages
- **Save buttons** for each content type
- **Confirmations** for critical actions

### 🔧 Performance Optimization:
- **Adaptive frame rate** (10-30 FPS depending on activity)
- **OCR caching** to avoid reprocessing
- **Smart memory cleanup** with worker control
- **Memory leak protection**

### 📝 Extended Logging:
- **Detailed logs** of all operations
- **Different logging levels** (DEBUG, INFO, WARNING, ERROR)
- **Log file rotation** by days
- **Error tracking** with stack trace

## 📋 Version Comparison

| Feature | Basic Version | Improved Version |
|---------|---------------|------------------|
| **OCR + Audio** | ✅ | ✅ |
| **OpenAI Integration** | ✅ | ✅ |
| **Hotkeys** | Ctrl+C | Ctrl+R, Ctrl+S, Esc, F1 |
| **Auto-save** | ❌ | ✅ (every 30 sec) |
| **Progress bars** | ❌ | ✅ |
| **Operation cancellation** | ❌ | ✅ |
| **Data export** | ❌ | ✅ (JSON/TXT) |
| **API validation** | ❌ | ✅ |
| **Logging** | ❌ | ✅ (4 levels) |
| **Session recovery** | ❌ | ✅ |
| **OCR caching** | ❌ | ✅ |
| **Adaptive FPS** | ❌ | ✅ (10-30 FPS) |
| **Context tooltips** | ❌ | ✅ |
| **Application menu** | ❌ | ✅ |

## 🎯 Version Selection Recommendations

### Use the **improved version** if:
- Working with important data (auto-save is critical)
- Need hotkeys for fast work
- Reliability and stability are required
- Detailed logs and error tracking are important
- Working for extended periods (performance optimization)

### Use the **basic version** if:
- Need simplicity without extra features
- Limited system resources
- One-time use

## Requirements

- Python 3.8+
- OpenAI API key (required for audio functions)
- PyAudio (for audio capture)
- OBS Studio with Virtual Camera (for OCR versions)
- Tesseract OCR (for OCR versions)
- Windows/Linux/macOS