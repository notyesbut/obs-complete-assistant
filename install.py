#!/usr/bin/env python3
"""
OBS Complete Assistant Installer Script
Easy installation script for the OBS Complete Assistant package.
"""

import os
import sys
import subprocess
import platform
import urllib.request
import json
from pathlib import Path

class Colors:
    """Terminal colors for better output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(message, color=Colors.OKGREEN):
    """Print colored message"""
    print(f"{color}{message}{Colors.ENDC}")

def print_header():
    """Print installation header"""
    print_colored("=" * 60, Colors.HEADER)
    print_colored("🚀 OBS Complete Assistant Installer", Colors.HEADER)
    print_colored("=" * 60, Colors.HEADER)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print_colored("🔍 Checking Python version...", Colors.OKBLUE)
    
    if sys.version_info < (3, 8):
        print_colored("❌ Python 3.8 or higher is required!", Colors.FAIL)
        print_colored(f"   Current version: {sys.version}", Colors.WARNING)
        return False
    
    print_colored(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected", Colors.OKGREEN)
    return True

def check_pip():
    """Check if pip is available"""
    print_colored("🔍 Checking pip availability...", Colors.OKBLUE)
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print_colored("✅ pip is available", Colors.OKGREEN)
        return True
    except subprocess.CalledProcessError:
        print_colored("❌ pip is not available!", Colors.FAIL)
        return False

def install_tesseract():
    """Provide instructions for Tesseract installation"""
    print_colored("🔍 Checking Tesseract OCR...", Colors.OKBLUE)
    
    system = platform.system().lower()
    
    print_colored("📋 Tesseract OCR Installation Instructions:", Colors.WARNING)
    
    if system == "windows":
        print_colored("   Windows:", Colors.OKCYAN)
        print_colored("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki", Colors.OKBLUE)
        print_colored("   2. Install the .exe file", Colors.OKBLUE)
        print_colored("   3. Add to PATH if needed", Colors.OKBLUE)
    elif system == "linux":
        print_colored("   Linux (Ubuntu/Debian):", Colors.OKCYAN)
        print_colored("   sudo apt-get update", Colors.OKBLUE)
        print_colored("   sudo apt-get install tesseract-ocr tesseract-ocr-rus", Colors.OKBLUE)
    elif system == "darwin":
        print_colored("   macOS:", Colors.OKCYAN)
        print_colored("   brew install tesseract tesseract-lang", Colors.OKBLUE)
    
    print()

def install_requirements():
    """Install Python requirements"""
    print_colored("📦 Installing Python dependencies...", Colors.OKBLUE)
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print_colored("✅ Python dependencies installed successfully", Colors.OKGREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Failed to install dependencies: {e}", Colors.FAIL)
        return False

def create_env_file():
    """Create .env file from example"""
    print_colored("🔧 Setting up environment file...", Colors.OKBLUE)
    
    if not os.path.exists(".env.example"):
        # Create .env.example if it doesn't exist
        env_example_content = """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Default settings
DEFAULT_MODEL=gpt-4o
DEFAULT_OCR_LANGUAGE=eng+rus
DEFAULT_WHISPER_LANGUAGE=en
DEFAULT_USER_NAME=User
"""
        with open(".env.example", "w") as f:
            f.write(env_example_content)
    
    if not os.path.exists(".env"):
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print_colored("✅ Created .env file from template", Colors.OKGREEN)
            print_colored("   📝 Remember to add your OpenAI API key to .env file", Colors.WARNING)
        except Exception as e:
            print_colored(f"❌ Failed to create .env file: {e}", Colors.FAIL)
    else:
        print_colored("✅ .env file already exists", Colors.OKGREEN)

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if platform.system().lower() != "windows":
        return
    
    print_colored("🖥️ Creating desktop shortcut...", Colors.OKBLUE)
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "OBS Complete Assistant.lnk")
        target = os.path.join(os.getcwd(), "obs_complete_assistant_optimized.py")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = os.getcwd()
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print_colored("✅ Desktop shortcut created", Colors.OKGREEN)
    except ImportError:
        print_colored("   ⚠️ winshell not available, skipping shortcut creation", Colors.WARNING)
    except Exception as e:
        print_colored(f"   ⚠️ Failed to create shortcut: {e}", Colors.WARNING)

def install_package():
    """Install the package in development mode"""
    print_colored("📦 Installing OBS Complete Assistant package...", Colors.OKBLUE)
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], check=True)
        print_colored("✅ Package installed successfully", Colors.OKGREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Failed to install package: {e}", Colors.FAIL)
        return False

def print_usage_instructions():
    """Print usage instructions"""
    print_colored("\n🎉 Installation Complete!", Colors.OKGREEN)
    print_colored("=" * 40, Colors.HEADER)
    
    print_colored("\n📋 How to run:", Colors.OKCYAN)
    print_colored("   python obs_assistant.py", Colors.OKGREEN)
    
    print_colored("\n⚙️ Setup Steps:", Colors.OKCYAN)
    print_colored("   1. Install Tesseract OCR (see instructions above)", Colors.OKBLUE)
    print_colored("   2. Add your OpenAI API key to .env file", Colors.OKBLUE)
    print_colored("   3. Start OBS and enable Virtual Camera", Colors.OKBLUE)
    print_colored("   4. Run the program", Colors.OKBLUE)
    
    print_colored("\n📚 Documentation:", Colors.OKCYAN)
    print_colored("   README.md (Russian) | README_EN.md (English)", Colors.OKBLUE)
    
    print_colored("\n🔑 Don't forget to:", Colors.WARNING)
    print_colored("   - Add your OpenAI API key to .env file", Colors.WARNING)
    print_colored("   - Install Tesseract OCR for your system", Colors.WARNING)

def main():
    """Main installation function"""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Show Tesseract installation instructions
    install_tesseract()
    
    # Install requirements
    if not install_requirements():
        print_colored("⚠️ Some dependencies failed to install. You may need to install them manually.", Colors.WARNING)
    
    # Setup environment
    create_env_file()
    
    # Install package
    install_package()
    
    # Create shortcuts (Windows only)
    if platform.system().lower() == "windows":
        create_desktop_shortcut()
    
    # Show usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n❌ Installation cancelled by user", Colors.FAIL)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ Installation failed: {e}", Colors.FAIL)
        sys.exit(1)