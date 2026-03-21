# Contributing to AIUCE

First off, thank you for considering contributing to AIUCE! It's people like you that make AIUCE such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to respectful, constructive collaboration. By participating, you are expected to uphold this standard.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what behavior you expected**
- **Include which layer(s) are involved** (L0-L10)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the enhancement**
- **Explain why this enhancement would be useful**
- **Specify which layer would benefit from this enhancement**

### Pull Requests

1. Fork the repository
2. Create a new branch from `main` (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests (`python -m pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/AIUCE.git
cd AIUCE

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Start development server
python api.py
```

## Layer Development Guide

### Adding a New Mind Model (L3)

```python
# In l3_reasoning.py
class MyMindModel:
    def analyze(self, input_data, context):
        # Your analysis logic
        return {"confidence": 0.8, "result": ...}

# Register in ReasoningLayer
reasoning.register_model("my_model", MyMindModel())
```

### Adding a New Data Source (L2)

```python
# In l2_perception.py
class MyDataSource:
    def fetch(self):
        # Your data fetching logic
        return data

perception.add_source("my_source", MyDataSource())
```

### Adding a New Tool (L9)

```python
# In l9_agent.py
class MyTool:
    def execute(self, params):
        # Your execution logic
        return result

agent.register_tool("my_tool", MyTool())
```

## Style Guidelines

### Python Code Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all public methods
- Keep functions focused and small

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Add constitutional check for data deletion

- Implement L0 veto for destructive operations
- Add audit logging for all constitution checks
- Update tests to cover new scenarios

Fixes #123
```

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

## Documentation

- Update README.md if you change functionality
- Update API documentation for API changes
- Add docstrings to new functions and classes

## Questions?

Feel free to open an issue with the `question` label or start a discussion.

Thank you for contributing! 🏯
