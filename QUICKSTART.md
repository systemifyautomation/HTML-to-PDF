# Quick Start Guide

This guide will help you get the HTML-to-PDF converter up and running in minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- System dependencies for WeasyPrint (see main README for details)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/systemifyautomation/HTML-to-PDF.git
cd HTML-to-PDF
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Test the API

### Using cURL

```bash
curl -X POST http://localhost:5000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Hello PDF!</h1></body></html>",
    "filename": "test.pdf"
  }' \
  --output test.pdf
```

### Using the Provided Examples

```bash
python examples/usage_example.py
```

This will generate several example PDFs including:
- Simple HTML document
- Styled document with custom CSS
- Invoice template
- Report template

## Next Steps

- Read the [full README](README.md) for detailed documentation
- Check out the example templates in the `examples/` directory
- Explore the API endpoints at `http://localhost:5000/`

## Common Issues

**Problem**: Module not found errors

**Solution**: Make sure you've installed all dependencies:
```bash
pip install --user -r requirements.txt
```

**Problem**: WeasyPrint installation fails

**Solution**: Install system dependencies first (see Prerequisites section in main README)

**Problem**: Port 5000 already in use

**Solution**: Use a different port:
```bash
PORT=8080 python app.py
```

## Getting Help

- Check the [Troubleshooting](README.md#-troubleshooting) section in the main README
- Open an issue on GitHub
- Run the test suite: `python test_api.py`
