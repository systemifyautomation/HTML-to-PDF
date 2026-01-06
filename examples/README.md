# Examples Directory

This directory contains example code and templates demonstrating how to use the HTML-to-PDF API.

## Files

### Python Examples

- **[usage_example.py](usage_example.py)** - Comprehensive Python examples showing:
  - Basic HTML to PDF conversion
  - Custom CSS styling
  - Loading HTML from files
  - Dynamic invoice generation with custom filenames
  - Date-based report filenames
  
### HTML Templates

- **[invoice_template.html](invoice_template.html)** - Professional invoice template
- **[report_template.html](report_template.html)** - Business report template
- **[simple_template.html](simple_template.html)** - Basic HTML template

### Screenshot Mode

- **[screenshot_mode_examples.py](screenshot_mode_examples.py)** - Examples for screenshot mode:
  - Auto-sized PDFs
  - Mobile viewport screenshots
  - Desktop viewport screenshots
  - Browser-like rendering

### Guides

- **[FILENAME_GUIDE.md](FILENAME_GUIDE.md)** - Complete guide to using custom filenames:
  - Dynamic filenames (invoices, reports, dates)
  - Security & sanitization
  - Best practices
  - Examples in Python, JavaScript, PHP

## Quick Start

### Run All Examples

```bash
# Make sure the API is running first
python app.py

# In another terminal, run the examples
python examples/usage_example.py
```

### Run Screenshot Examples

```bash
python examples/screenshot_mode_examples.py
```

## Using Custom Filenames

All examples demonstrate the `filename` parameter:

```python
import requests

response = requests.post(
    'http://localhost:5000/convert',
    headers={'X-API-Key': 'YOUR_API_KEY'},
    json={
        'html': '<h1>Invoice #12345</h1>',
        'filename': 'invoice-12345.pdf'  # Custom filename!
    }
)
```

**See [FILENAME_GUIDE.md](FILENAME_GUIDE.md) for complete documentation.**

## Example: Dynamic Invoice Filename

```python
# Generate invoice with dynamic filename
invoice_id = "INV-2024-001"
customer_name = "Acme Corp"
date = "2024-01-06"

filename = f"invoice-{invoice_id}-{customer_name}-{date}.pdf"

response = requests.post(url, json={
    'html': invoice_html,
    'filename': filename
})

# Saves as: invoice-INV-2024-001-Acme Corp-2024-01-06.pdf
```

## API Key Setup

Before running examples, make sure you have:

1. **Generated API keys**: Run `python generate_api_key.py`
2. **Updated examples**: Replace `your-api-key-here` with your actual key
3. **Started the API**: Run `python app.py`

## More Information

- [Main README](../README.md)
- [API Documentation](../README.md#-api-documentation)
- [Deployment Guide](../PRODUCTION_DEPLOYMENT.md)
