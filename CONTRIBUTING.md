# Contributing to HTML-to-PDF Converter

Thank you for your interest in contributing to the HTML-to-PDF Converter project! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear description of the bug
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

We welcome feature requests! Please open an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Any implementation ideas you might have

### Submitting Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if applicable
4. **Update documentation** to reflect your changes
5. **Test your changes** thoroughly
6. **Submit a pull request** with a clear description

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/HTML-to-PDF.git
cd HTML-to-PDF
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the test suite:
```bash
python test_api.py
```

## Coding Standards

- Follow PEP 8 style guidelines for Python code
- Write clear, descriptive commit messages
- Include docstrings for functions and classes
- Keep functions focused and modular
- Add comments for complex logic

## Testing

- Ensure all existing tests pass before submitting a PR
- Add tests for new features
- Test error handling and edge cases
- Verify documentation accuracy

## Documentation

When adding new features:
- Update the README.md with usage examples
- Add docstrings to new functions
- Update API documentation if endpoints change
- Include examples when helpful

## Code Review Process

1. A maintainer will review your pull request
2. Address any feedback or requested changes
3. Once approved, a maintainer will merge your PR

## Questions?

Feel free to open an issue if you have questions about contributing!

## Code of Conduct

Be respectful and professional in all interactions. We aim to foster an inclusive and welcoming community.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
