# Contributing to AIUCE 🏯

First off, thank you for considering contributing to AIUCE! It's people like you that make AIUCE such a great tool.

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## 🤔 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what you expected**
- **Include screenshots or animated GIFs if helpful**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain the desired behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible
- Follow the Python style guide (PEP 8)
- Include tests for new functionality
- Update documentation for changed functionality
- End all files with a newline

---

## 🛠️ Development Process

### Setting Up Your Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/aiuce.git
cd aiuce

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest tests/
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test file
pytest tests/test_l0_constitution.py

# Run with verbose output
pytest -v tests/
```

### Code Style

We follow PEP 8 style guidelines. Use these tools to ensure consistency:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check with flake8
flake8 .

# Type checking with mypy
mypy aiuce/
```

### Commit Messages

Follow these guidelines for commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(L0): add constitutional veto for high-risk operations

Add L0 layer capability to veto any action that violates
the constitution. This ensures AI stays under control.

Closes #42
```

```
fix(L5): correct timestamp format in decision log

The decision log was using incorrect ISO format.
Now uses proper ISO 8601 format with timezone.

Fixes #87
```

---

## 🏗️ Architecture Guidelines

### Adding a New Layer

If you want to add or modify a layer, follow these steps:

1. **Read the Architecture Documentation** (docs/architecture.md)
2. **Understand the Data Flow** (docs/architecture_diagrams.md)
3. **Follow the Layer Template**:
   ```python
   # lX_layername.py
   
   class LXLayerName:
       def __init__(self, config):
           self.config = config
       
       def process(self, input_data):
           """Process input according to layer responsibility."""
           # Implementation
           return output_data
   ```
4. **Write Tests** (tests/test_lX_layername.py)
5. **Update Documentation**

### Modifying Existing Layers

1. **Ensure backward compatibility** when possible
2. **Add deprecation warnings** if breaking changes needed
3. **Update all related tests**
4. **Update documentation**

---

## 📚 Documentation Guidelines

### What to Document

- **API Reference**: All public functions and classes
- **Architecture**: Design decisions and rationale
- **Examples**: How to use the system
- **Tutorials**: Step-by-step guides

### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Keep it up-to-date with code changes

---

## 🔍 Review Process

1. **Automated Checks**: CI runs tests, linting, and type checking
2. **Code Review**: At least one maintainer reviews the PR
3. **Discussion**: We discuss any questions or concerns
4. **Approval**: Maintainer approves the PR
5. **Merge**: PR is merged into main branch

---

## 🏆 Recognition

Contributors are recognized in:

- **README.md**: All contributors listed
- **CHANGELOG.md**: Significant contributions mentioned
- **GitHub Contributors**: Automatic recognition

---

## ❓ Questions?

- **GitHub Discussions**: For general questions
- **GitHub Issues**: For bug reports and feature requests
- **Email**: For private inquiries (see profile)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AIUCE! 🏯

*Bringing Ancient Wisdom to Modern AI*
