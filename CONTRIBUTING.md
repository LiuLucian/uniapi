# Contributing to UniAPI

Thank you for your interest in contributing to UniAPI! This document provides guidelines for contributing to the project.

## 🐛 Found a Bug?

1. **Search existing issues first** - Your bug might already be reported
2. **Use the bug report template** when creating a new issue
3. **Include reproduction steps** - Help us reproduce the problem:
   - Platform (Instagram/TikTok/Twitter/Facebook/LinkedIn)
   - Python version
   - Error message/stack trace
   - Steps to reproduce

## 💡 Have an Idea?

1. **Check discussions first** - Someone might have suggested it already
2. **Open a new discussion** in the Ideas category
3. **Describe the use case** - Why would this feature be useful?
4. **Wait for feedback** before starting to code

## 🔧 Want to Contribute Code?

### Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/uniapi.git
   cd uniapi
   ```
3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Setup

```bash
cd backend
./install.sh
```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Testing Your Changes

Before submitting:

1. **Test locally**:
   ```bash
   cd backend
   ./start_uniapi.sh
   ```
2. **Test the affected platform**:
   ```python
   from instagram_sdk import InstagramAPI
   api = InstagramAPI()
   # Test your changes
   ```
3. **Check for errors** in the console output

### Commit Messages

Use clear, descriptive commit messages:

- ✅ `feat: Add TikTok video upload support`
- ✅ `fix: Instagram DM sending timeout issue`
- ✅ `docs: Update quick start guide`
- ❌ `update code`
- ❌ `fix bug`

### Submitting a Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
2. **Open a Pull Request** on GitHub
3. **Describe your changes**:
   - What does this PR do?
   - Why is this change needed?
   - How did you test it?
4. **Link related issues** using `Fixes #123`

## 🏷️ Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature request
- `good first issue` - Good for newcomers
- `help wanted` - Community help needed
- `documentation` - Documentation improvements

## 📝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help newcomers learn

## ❓ Questions?

- Open a [Discussion](https://github.com/LiuLucian/uniapi/discussions) for questions
- Tag with `Q&A` category

## 🎉 Recognition

Contributors will be:
- Listed in the README (if they want)
- Mentioned in release notes
- Given credit in relevant documentation

Thank you for making UniAPI better! 🚀
