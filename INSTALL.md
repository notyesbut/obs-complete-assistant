# 🚀 OBS Complete Assistant - Installation Guide

Easy installation guide for OBS Complete Assistant with multiple installation methods.

## 📋 Prerequisites

- **Python 3.8+** - [Download from python.org](https://python.org)
- **OpenAI API Key** - [Get from OpenAI](https://platform.openai.com/api-keys)
- **OBS Studio** - [Download from obsproject.com](https://obsproject.com)
- **Tesseract OCR** - See platform-specific instructions below

## 🎯 Quick Installation

### Method 1: Auto-Installer (Recommended)

#### Windows:
```bash
# Double-click install.bat or run in Command Prompt:
install.bat
```

#### Linux/macOS:
```bash
# Make executable and run:
chmod +x install.sh
./install.sh
```

#### Cross-platform Python installer:
```bash
python install.py
```

### Method 2: Manual Installation

1. **Clone or download** this repository
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Tesseract OCR** (see platform instructions below)
4. **Configure API key** (see configuration section)

### Method 3: Package Installation

```bash
# Install as a package (development mode)
pip install -e .

# Run from anywhere
obs-assistant
```

## 🔧 Platform-Specific Setup

### Windows
1. **Tesseract OCR:**
   - Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install the `.exe` file
   - Add to PATH or set in `.env` file

2. **Optional - Visual C++ Redistributable:**
   - May be needed for some dependencies

### Linux (Ubuntu/Debian)
```bash
# Install Tesseract OCR
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-rus tesseract-ocr-deu

# Install system dependencies
sudo apt-get install python3-dev python3-pip portaudio19-dev
```

### macOS
```bash
# Install Tesseract OCR
brew install tesseract tesseract-lang

# Install system dependencies
brew install portaudio
```

## ⚙️ Configuration

### 1. OpenAI API Key Setup

#### Option A: Environment File (Recommended)
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` file and add your API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

#### Option B: Through Application
- Launch the application
- Go to Settings tab
- Enter your API key in the "OpenAI API Key" field

### 2. Tesseract Path (if needed)
If Tesseract is not in your system PATH, add to `.env`:
```
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## 🚀 Running the Application

### Main Application:
```bash
python obs_assistant.py
```

Features:
- ✅ Floating windows
- ✅ Video OCR with OBS integration
- ✅ Real-time audio transcription
- ✅ Interview assistant mode
- ✅ OpenAI API integration
- ✅ All optimizations included

### Command Line (after package install):
```bash
obs-assistant
```

## 🔍 Troubleshooting

### Common Issues:

#### 1. "No module named 'cv2'"
```bash
pip install opencv-python
```

#### 2. "Tesseract not found"
- Install Tesseract OCR for your platform
- Add to PATH or configure in `.env`

#### 3. "PyQt5 installation failed"
```bash
# Try installing system packages first (Linux)
sudo apt-get install python3-pyqt5

# Or use conda
conda install pyqt
```

#### 4. "sounddevice not working"
```bash
# Linux - install ALSA development files
sudo apt-get install libasound2-dev

# macOS - install portaudio
brew install portaudio
```

#### 5. "OpenAI API errors"
- Check your API key is valid
- Ensure you have credits in your OpenAI account
- Check your API usage limits

### System Requirements:
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB free space
- **Internet:** Required for OpenAI API calls
- **Camera:** OBS Virtual Camera or DirectShow device

## 📚 Post-Installation

### 1. Setup OBS:
1. Install OBS Studio
2. Set up your scenes
3. Start Virtual Camera (Tools → Virtual Camera)

### 2. First Run:
1. Launch the application
2. Go to Settings tab
3. Configure your preferences:
   - OpenAI API Key
   - OCR Language
   - Audio settings
   - Interview mode (if needed)

### 3. Test Features:
- **Video OCR:** Select area with mouse, zoom with wheel
- **Audio:** Click record button, speak into microphone
- **Quick Responses:** Type question in floating window

## 🆘 Getting Help

### Documentation:
- **English:** [README_EN.md](README_EN.md)
- **Russian:** [README.md](README.md)

### Support:
- Check the troubleshooting section above
- Review the requirements and ensure all dependencies are installed
- Check the issues section if using from GitHub

### System Information:
To help with troubleshooting, gather this information:
```bash
python --version
pip list | grep -E "(opencv|pyqt|tesseract|openai)"
tesseract --version
```

## 🎉 Success!

Once installed, you should have:
- ✅ All Python dependencies installed
- ✅ Tesseract OCR configured
- ✅ OpenAI API key set up
- ✅ Application ready to run

Launch with your preferred version and enjoy using OBS Complete Assistant!