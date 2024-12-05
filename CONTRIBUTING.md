# Contributing to ConfigBuddy 🚀

First off, thanks for taking the time to contribute! ❤️

## 📝 Code of Conduct

TODO

## 🌟 How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include code samples and error messages if applicable

### Suggesting Enhancements ✨

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- A clear and descriptive title
- A detailed description of the proposed functionality
- Explain why this enhancement would be useful
- List any similar features in other projects if applicable
- Include mockups or examples if possible

### Pull Requests 💪

- Fork the repo and create your branch from `main`
- If you've added code that should be tested, add tests
- Ensure the test suite passes
- Make sure your code follows the existing code style
- Include appropriate documentation
- Issue that pull request!

## 🔧 Development Setup

1. Fork and clone the repo

   ```bash
   git clone https://github.com/your-username/configbuddy.git
   ```

2. Create a virtual environment and activate it

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies

   ```bash
   pip install -e ".[test]"
   ```

4. Install pre-commit hooks
   ```bash
   pre-commit install
   ```

## 🧪 Running Tests

```bash
pytest
```

For coverage report:

```bash
pytest --cov=configbuddy
```

## 📋 Style Guide

- Use [mypy](https://github.com/python/mypy) for type checking and [ruff](https://github.com/astral-sh/ruff) for code formatting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Write docstrings in Google style
- Type hints are required for all functions
- Keep functions focused and small
- Write meaningful commit messages

## 📚 Documentation

- Keep docstrings up to date
- Update README.md if needed
- Add comments for complex logic
- Include type hints and examples

## 🏷️ Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## 🎯 Project Structure

```
configbuddy/
├── src/
│   └── configbuddy/
│       ├── core/           # Core functionality
│       ├── cli/           # CLI interface (TODO)
│       └── web/           # Web interface (TODO)
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
└── docs/                # Documentation
```

## ✅ Pull Request Checklist

Before submitting your PR, please review this checklist:

- [ ] Code follows style guidelines
- [ ] Tests are added/updated and passing
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] Type hints are included
- [ ] Code is commented where necessary
- [ ] Branch is up to date with main

## 📬 Questions?

Feel free to open an issue or contact the maintainers if you have any questions!

---

Thank you for contributing to ConfigBuddy! 🎉
