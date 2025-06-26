#!/bin/bash

# OBS Complete Assistant - Linux/macOS Installer

echo "==============================================="
echo "   OBS Complete Assistant - Unix Installer"
echo "==============================================="
echo

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python $python_version found!"

# Check if version is 3.8+
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "ERROR: Python 3.8+ is required"
    exit 1
fi

echo "Running installer..."
python3 install.py

if [ $? -ne 0 ]; then
    echo
    echo "Installation failed. Please check the error messages above."
    exit 1
fi

echo
echo "Installation completed successfully!"
echo "You can now run the program with: python3 obs_assistant.py"
echo

# Make the main script executable
chmod +x obs_assistant.py

echo "Scripts made executable."