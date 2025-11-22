# Contributing to MedCare System

Thank you for your interest in contributing to MedCare System! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/medcare-system.git
cd medcare-system

# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused on a single task
- Write comments for complex logic

## Testing

Before submitting a pull request:
- Test all API endpoints using `/docs`
- Verify frontend functionality
- Check for any console errors
- Ensure no breaking changes to existing features

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the requirements.txt if you add dependencies
3. Ensure your code follows the existing style
4. Write clear commit messages
5. Reference any related issues in your PR description

## Reporting Bugs

When reporting bugs, please include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, etc.)

## Feature Requests

We welcome feature requests! Please:
- Check if the feature has already been requested
- Provide a clear description of the feature
- Explain why it would be useful
- Include examples of how it would work

## Questions?

Feel free to open an issue for questions or discussions about the project.

Thank you for contributing! 🎉