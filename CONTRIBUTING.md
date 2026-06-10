# Contributing to Iraqi Arabic NLP Toolkit

First off, thank you for considering contributing to IANLP! It's people like you that make this toolkit such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python style guide
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline

## Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Iraqi-Arabic-NLP-Toolkit-IANLP-.git
   cd Iraqi-Arabic-NLP-Toolkit-IANLP-
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Make your changes and commit**
   ```bash
   git add .
   git commit -m "Add descriptive commit message"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**

## Style Guide

### Python Style

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use type hints for function parameters and returns
* Write docstrings for all public functions and classes
* Use meaningful variable names
* Keep functions focused and concise

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Documentation

* Use clear, concise language
* Include code examples where appropriate
* Update README.md if adding new features
* Add docstrings to all modules and functions

## Testing

* Write tests for new functionality
* Ensure all tests pass before submitting PR
* Aim for at least 80% code coverage
* Run tests locally: `pytest tests/`

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested

## Questions?

Feel free to contact the project maintainers:
- **Hussein Hadi** - hussainhade12345@gmail.com

Thank you for contributing! 🎉
