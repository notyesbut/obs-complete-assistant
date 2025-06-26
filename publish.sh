#!/bin/bash

# OBS Complete Assistant - GitHub Publishing Script
# This script prepares and publishes the project to GitHub

echo "🚀 OBS Complete Assistant - GitHub Publisher"
echo "============================================="
echo

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    echo "   Download from: https://git-scm.com/"
    exit 1
fi

echo "✅ Git is available"

# Get GitHub repository URL from user
echo
echo "📝 Please provide your GitHub repository details:"
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter repository name (default: obs-complete-assistant): " REPO_NAME
REPO_NAME=${REPO_NAME:-obs-complete-assistant}

GITHUB_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo
echo "🔗 Repository URL: $GITHUB_URL"
echo

# Confirm with user
read -p "Continue with this repository? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled by user"
    exit 1
fi

echo
echo "🔄 Initializing Git repository..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Configure git user if not set
if [ -z "$(git config user.name)" ]; then
    read -p "Enter your name for Git commits: " GIT_NAME
    git config user.name "$GIT_NAME"
fi

if [ -z "$(git config user.email)" ]; then
    read -p "Enter your email for Git commits: " GIT_EMAIL
    git config user.email "$GIT_EMAIL"
fi

echo "✅ Git user configured"

# Add all files
echo
echo "📁 Adding files to repository..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "⚠️  No changes to commit"
else
    echo "✅ Files added to staging area"
    
    # Create initial commit
    echo
    echo "💾 Creating initial commit..."
    git commit -m "feat: initial release v1.0.0 - OBS Complete Assistant

🎉 Complete OBS Virtual Camera assistant with OCR and audio features

Features:
- 📹 Video OCR with OBS Virtual Camera integration  
- 🎤 Real-time audio transcription via OpenAI Whisper
- 🧠 Interview assistant mode with specialized prompts
- 🪟 Floating windows for better organization
- ⚙️ Multi-threaded processing and optimizations

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    echo "✅ Initial commit created"
fi

# Set main branch
echo
echo "🌿 Setting up main branch..."
git branch -M main
echo "✅ Main branch configured"

# Add remote origin
echo
echo "🔗 Adding remote repository..."
if git remote | grep -q origin; then
    git remote set-url origin "$GITHUB_URL"
    echo "✅ Remote origin updated"
else
    git remote add origin "$GITHUB_URL"
    echo "✅ Remote origin added"
fi

# Push to GitHub
echo
echo "🚀 Publishing to GitHub..."
echo "📋 Make sure you have:"
echo "   1. Created the repository on GitHub: $GITHUB_URL"
echo "   2. Set up authentication (GitHub token or SSH key)"
echo

read -p "Ready to push to GitHub? (y/N): " PUSH_CONFIRM
if [[ $PUSH_CONFIRM =~ ^[Yy]$ ]]; then
    if git push -u origin main; then
        echo
        echo "🎉 Successfully published to GitHub!"
        echo "🔗 Repository URL: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
        echo
        echo "📋 Next steps:"
        echo "   1. Go to your repository on GitHub"
        echo "   2. Create a release (v1.0.0) from the releases tab"
        echo "   3. Configure repository settings and topics"
        echo "   4. Enable GitHub Actions (already configured)"
        echo
        echo "🏷️ Suggested repository topics:"
        echo "   obs, ocr, speech-to-text, openai, python, pyqt5, virtual-camera"
    else
        echo
        echo "❌ Failed to push to GitHub"
        echo "📋 Common solutions:"
        echo "   1. Make sure the repository exists on GitHub"
        echo "   2. Check your authentication (token/SSH key)"
        echo "   3. Verify the repository URL is correct"
        echo "   4. Try: git push --set-upstream origin main"
    fi
else
    echo "⏸️  Push cancelled. Repository is ready for manual push:"
    echo "   git push -u origin main"
fi

echo
echo "📁 Repository status:"
git status

echo
echo "🔚 Script completed!"