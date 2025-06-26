@echo off
echo ===============================================
echo    OBS Complete Assistant - Windows Installer
echo ===============================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found! Running installer...
python install.py

if errorlevel 1 (
    echo.
    echo Installation failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo You can now run the program with: python obs_assistant.py
echo.
pause