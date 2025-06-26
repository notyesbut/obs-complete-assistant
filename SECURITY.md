# Security Policy

## 🔒 Supported Versions

We actively maintain security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ Yes            |
| < 1.0   | ❌ No             |

## 🚨 Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please:

1. **Email us directly** at: security@obsassistant.com
2. **Include the following information:**
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Your contact information
   - Any suggested fixes (optional)

### What to Expect

- **Acknowledgment:** We'll acknowledge receipt within 48 hours
- **Assessment:** We'll assess the vulnerability within 7 days
- **Timeline:** We'll provide a timeline for fixes
- **Updates:** We'll keep you informed of our progress
- **Credit:** We'll credit you in the security advisory (if desired)

## 🛡️ Security Measures

### Current Security Practices

#### API Key Protection:
- ✅ API keys stored in environment variables
- ✅ API keys never logged or displayed
- ✅ Support for `.env` files with proper gitignore
- ✅ Clear warnings about API key security

#### Data Security:
- ✅ Local data storage only (no cloud by default)
- ✅ Temporary files cleaned up automatically
- ✅ Audio data processed locally
- ✅ OCR processing happens locally

#### Network Security:
- ✅ HTTPS for all OpenAI API calls
- ✅ No unnecessary network requests
- ✅ Proper SSL certificate validation
- ✅ Timeout protection for API calls

#### Code Security:
- ✅ Input validation for user data
- ✅ Sanitization of file paths
- ✅ Protection against path traversal
- ✅ Safe handling of external processes

## ⚠️ Known Security Considerations

### API Key Management:
- **Risk:** API keys in plain text
- **Mitigation:** Use environment variables, never commit keys
- **User responsibility:** Keep API keys secure

### Screen Capture:
- **Risk:** Sensitive information in OCR screenshots
- **Mitigation:** Local processing only, temporary files cleaned
- **User responsibility:** Be aware of what's being captured

### Audio Recording:
- **Risk:** Sensitive conversations recorded
- **Mitigation:** Local processing, user controls recording
- **User responsibility:** Use in appropriate settings

### File System Access:
- **Risk:** Application has file system access
- **Mitigation:** Limited to necessary directories only
- **User responsibility:** Run with appropriate permissions

## 🔧 Security Best Practices for Users

### API Keys:
- ✅ **DO:** Store in `.env` file
- ✅ **DO:** Use environment variables
- ✅ **DO:** Rotate keys periodically
- ❌ **DON'T:** Commit keys to version control
- ❌ **DON'T:** Share keys publicly
- ❌ **DON'T:** Use keys in shared environments

### Usage:
- ✅ **DO:** Use in trusted environments
- ✅ **DO:** Be aware of what's being captured
- ✅ **DO:** Keep software updated
- ❌ **DON'T:** Use on shared/public computers
- ❌ **DON'T:** Capture sensitive/confidential information
- ❌ **DON'T:** Leave recordings unattended

### System Security:
- ✅ **DO:** Keep Python and dependencies updated
- ✅ **DO:** Use antivirus software
- ✅ **DO:** Run with minimal necessary permissions
- ❌ **DON'T:** Run as administrator/root unless necessary
- ❌ **DON'T:** Disable security software
- ❌ **DON'T:** Ignore security warnings

## 🛠️ For Developers

### Secure Coding Guidelines:

#### Input Validation:
```python
# Always validate user inputs
def validate_api_key(key):
    if not key or len(key) < 10:
        raise ValueError("Invalid API key format")
    return key.strip()
```

#### File Operations:
```python
# Sanitize file paths
import os
def safe_file_path(user_path):
    # Prevent path traversal attacks
    clean_path = os.path.normpath(user_path)
    if '..' in clean_path:
        raise ValueError("Invalid file path")
    return clean_path
```

#### API Calls:
```python
# Always use HTTPS and validate certificates
import requests
response = requests.get(url, verify=True, timeout=30)
```

### Security Testing:
- Test with invalid inputs
- Verify API key protection
- Check file path validation
- Test network timeout handling
- Validate temporary file cleanup

## 📋 Security Checklist for Contributors

Before submitting code:

- [ ] No hardcoded API keys or secrets
- [ ] Input validation implemented
- [ ] File paths properly sanitized
- [ ] Network requests use HTTPS
- [ ] Temporary files cleaned up
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies are up to date
- [ ] No unnecessary permissions requested

## 🚫 Out of Scope

The following are considered out of scope for security reports:

- Issues in third-party dependencies (report to upstream)
- Social engineering attacks
- Physical access to user's machine
- Issues requiring admin/root privileges
- Denial of service through resource exhaustion
- Issues in development/debug modes

## 📞 Contact Information

For security-related inquiries:
- **Email:** security@obsassistant.com
- **Response time:** Within 48 hours
- **Languages:** English, Russian

For general support:
- **GitHub Issues:** For non-security bugs
- **GitHub Discussions:** For questions and support

## 🏆 Security Hall of Fame

We appreciate researchers who responsibly disclose security vulnerabilities:

*No vulnerabilities reported yet*

---

**Remember:** Security is a shared responsibility. We're committed to maintaining a secure application, but users must also follow best practices to protect their data and API keys.