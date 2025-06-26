@echo off
setlocal enabledelayedexpansion

REM OBS Complete Assistant - GitHub Publishing Script (Windows)
REM This script prepares and publishes the project to GitHub

echo ================================================
echo   OBS Complete Assistant - GitHub Publisher
echo ================================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed. Please install Git first.
    echo Download from: https://git-scm.com/
    pause
    exit /b 1
)

echo Git is available
echo.

REM Get GitHub repository details
echo Please provide your GitHub repository details:
set /p GITHUB_USERNAME="Enter your GitHub username: "
set /p REPO_NAME="Enter repository name (default: obs-complete-assistant): "
if "%REPO_NAME%"=="" set REPO_NAME=obs-complete-assistant

set GITHUB_URL=https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

echo.
echo Repository URL: %GITHUB_URL%
echo.

set /p CONFIRM="Continue with this repository? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled by user
    pause
    exit /b 1
)

echo.
echo Initializing Git repository...

REM Initialize git if not already done
if not exist ".git" (
    git init
    echo Git repository initialized
) else (
    echo Git repository already exists
)

REM Configure git user if not set
for /f "tokens=*" %%i in ('git config user.name 2^>nul') do set GIT_USER_NAME=%%i
if "%GIT_USER_NAME%"=="" (
    set /p GIT_NAME="Enter your name for Git commits: "
    git config user.name "!GIT_NAME!"
)

for /f "tokens=*" %%i in ('git config user.email 2^>nul') do set GIT_USER_EMAIL=%%i
if "%GIT_USER_EMAIL%"=="" (
    set /p GIT_EMAIL="Enter your email for Git commits: "
    git config user.email "!GIT_EMAIL!"
)

echo Git user configured
echo.

REM Add all files
echo Adding files to repository...
git add .

REM Check if there are changes to commit
git diff --staged --quiet
if errorlevel 1 (
    echo Files added to staging area
    echo.
    
    REM Create initial commit
    echo Creating initial commit...
    git commit -m "feat: initial release v1.0.0 - OBS Complete Assistant" -m "" -m "Complete OBS Virtual Camera assistant with OCR and audio features" -m "" -m "Features:" -m "- Video OCR with OBS Virtual Camera integration" -m "- Real-time audio transcription via OpenAI Whisper" -m "- Interview assistant mode with specialized prompts" -m "- Floating windows for better organization" -m "- Multi-threaded processing and optimizations" -m "" -m "Generated with Claude Code" -m "" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
    
    echo Initial commit created
) else (
    echo No changes to commit
)

REM Set main branch
echo.
echo Setting up main branch...
git branch -M main
echo Main branch configured

REM Add remote origin
echo.
echo Adding remote repository...
git remote | findstr origin >nul
if errorlevel 1 (
    git remote add origin %GITHUB_URL%
    echo Remote origin added
) else (
    git remote set-url origin %GITHUB_URL%
    echo Remote origin updated
)

REM Push to GitHub
echo.
echo Publishing to GitHub...
echo Make sure you have:
echo    1. Created the repository on GitHub: %GITHUB_URL%
echo    2. Set up authentication (GitHub token or SSH key)
echo.

set /p PUSH_CONFIRM="Ready to push to GitHub? (y/N): "
if /i "%PUSH_CONFIRM%"=="y" (
    git push -u origin main
    if errorlevel 1 (
        echo.
        echo Failed to push to GitHub
        echo Common solutions:
        echo    1. Make sure the repository exists on GitHub
        echo    2. Check your authentication (token/SSH key)
        echo    3. Verify the repository URL is correct
        echo    4. Try: git push --set-upstream origin main
    ) else (
        echo.
        echo Successfully published to GitHub!
        echo Repository URL: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
        echo.
        echo Next steps:
        echo    1. Go to your repository on GitHub
        echo    2. Create a release (v1.0.0) from the releases tab
        echo    3. Configure repository settings and topics
        echo    4. Enable GitHub Actions (already configured)
        echo.
        echo Suggested repository topics:
        echo    obs, ocr, speech-to-text, openai, python, pyqt5, virtual-camera
    )
) else (
    echo Push cancelled. Repository is ready for manual push:
    echo    git push -u origin main
)

echo.
echo Repository status:
git status

echo.
echo Script completed!
pause