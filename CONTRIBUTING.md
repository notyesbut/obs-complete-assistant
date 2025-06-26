# Contributing to OBS Complete Assistant

Thank you for your interest in contributing to OBS Complete Assistant! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues
- Use the [Issues](https://github.com/obs-assistant/obs-complete-assistant/issues) section to report bugs
- Provide detailed information about your system and the issue
- Include steps to reproduce the problem
- Add screenshots or logs if applicable

### Suggesting Features
- Open an issue with the "enhancement" label
- Clearly describe the feature and its use case
- Explain why it would be beneficial to other users

### Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## 🔧 Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/obs-assistant/obs-complete-assistant.git
   cd obs-complete-assistant
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e .[dev]
   ```

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Add your OpenAI API key to .env
   ```

## 📝 Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Comment complex logic
- Keep functions focused and small

### Code Formatting
```bash
# Format code with black
black obs_assistant.py

# Check with flake8
flake8 obs_assistant.py

# Type checking with mypy
mypy obs_assistant.py
```

## 🧪 Testing

- Test your changes on multiple platforms if possible
- Ensure all existing functionality still works
- Test with different OpenAI models
- Verify OCR functionality with various text types
- Test audio recording and transcription

## 📚 Documentation

- Update README.md if adding new features
- Update INSTALL.md for installation changes
- Add comments to complex code sections
- Update version numbers when appropriate

## 🎯 Areas for Contribution

### High Priority:
- **Performance optimization** - Speed up OCR and audio processing
- **Error handling** - Better error messages and recovery
- **UI improvements** - Enhanced user interface elements
- **Cross-platform testing** - Ensure compatibility across OS

### Medium Priority:
- **New OCR languages** - Support for additional languages
- **Audio formats** - Support for more audio input/output formats
- **Export options** - Additional data export formats
- **Keyboard shortcuts** - More hotkey combinations

### Low Priority:
- **Themes** - Dark/light theme support
- **Plugins** - Plugin system for extensions
- **Cloud integration** - Cloud storage for settings/history

## 🚫 What Not to Contribute

- **Malicious code** - No security vulnerabilities or backdoors
- **API key exposure** - Never commit API keys or secrets
- **Breaking changes** - Avoid changes that break existing functionality
- **Bloatware** - Keep the application focused and lightweight

## 📋 Pull Request Guidelines

### Before Submitting:
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No API keys or secrets committed
- [ ] Feature works on your local system

### PR Description Should Include:
- Clear description of changes
- Reason for the changes
- Screenshots/videos for UI changes
- Testing steps performed
- Any breaking changes

## 🐛 Bug Report Template

```markdown
**Bug Description:**
A clear description of the bug.

**Steps to Reproduce:**
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior:**
What should happen.

**Screenshots:**
If applicable, add screenshots.

**System Information:**
- OS: [e.g. Windows 10]
- Python version: [e.g. 3.9.0]
- Application version: [e.g. 1.0.0]

**Additional Context:**
Any other relevant information.
```

## 💡 Feature Request Template

```markdown
**Feature Description:**
A clear description of the feature.

**Use Case:**
Why would this feature be useful?

**Proposed Solution:**
How should this feature work?

**Alternatives:**
Any alternative solutions considered?

**Additional Context:**
Any other relevant information.
```

## 🏷️ Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: add new OCR language support for Japanese
fix: resolve audio recording buffer overflow issue
docs: update installation instructions for macOS
refactor: optimize video frame processing performance
```

### Commit Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Maintenance tasks

## 🎉 Recognition

Contributors will be:
- Listed in the project's contributors section
- Mentioned in release notes for significant contributions
- Given appropriate credit in documentation

## 📞 Getting Help

- **Issues:** Use GitHub Issues for bug reports and feature requests
- **Discussions:** Use GitHub Discussions for general questions
- **Email:** Contact maintainers directly for sensitive issues

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

Thank you for helping make OBS Complete Assistant better! 🚀