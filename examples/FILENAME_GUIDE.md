# Filename Parameter Guide

## Overview

The `filename` parameter allows you to control the name of the downloaded PDF file. This is particularly useful for:
- Dynamic invoice numbers
- Date-based reports
- User-specific documents
- Automated document generation

## Basic Usage

### Simple Example

```bash
curl -X POST https://your-domain.com/convert \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<h1>Invoice</h1><p>Total: $500</p>",
    "filename": "invoice-12345.pdf"
  }' \
  --output invoice.pdf
```

### Python Example

```python
import requests

response = requests.post(
    'https://your-domain.com/convert',
    headers={'X-API-Key': 'YOUR_API_KEY'},
    json={
        'html': '<h1>Invoice</h1><p>Total: $500</p>',
        'filename': 'invoice-12345.pdf'
    }
)

# The filename controls the Content-Disposition header
# Save locally with any name you want
with open('my-local-copy.pdf', 'wb') as f:
    f.write(response.content)
```

## Dynamic Filenames

### Date-Based Filenames

```python
from datetime import datetime

date_str = datetime.now().strftime("%Y-%m-%d")
filename = f"report-{date_str}.pdf"

response = requests.post(url, json={
    'html': report_html,
    'filename': filename  # e.g., "report-2026-01-06.pdf"
})
```

### Invoice Numbers

```python
invoice_number = "INV-2024-12345"
filename = f"invoice-{invoice_number}.pdf"

response = requests.post(url, json={
    'html': invoice_html,
    'filename': filename  # e.g., "invoice-INV-2024-12345.pdf"
})
```

### User-Specific Documents

```python
user_id = "john_doe"
document_type = "statement"
filename = f"{user_id}-{document_type}.pdf"

response = requests.post(url, json={
    'html': statement_html,
    'filename': filename  # e.g., "john_doe-statement.pdf"
})
```

### Timestamp-Based Filenames

```python
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"screenshot-{timestamp}.pdf"

response = requests.post(url, json={
    'html': screenshot_html,
    'filename': filename  # e.g., "screenshot-20260106_143022.pdf"
})
```

## Security & Validation

The API automatically **sanitizes** filenames for security:

### What Gets Sanitized

- **Path separators** removed: `../../malicious.pdf` → `malicious.pdf`
- **Special characters** removed: `file<>|?.pdf` → `file.pdf`
- **Only allowed**: Letters, numbers, spaces, dots, hyphens, underscores

### Examples

| Input Filename | Sanitized Output |
|----------------|------------------|
| `invoice 2024.pdf` | `invoice 2024.pdf` ✅ |
| `../../../etc/passwd` | `etcpasswd.pdf` ✅ |
| `report<script>.pdf` | `reportscript.pdf` ✅ |
| `file|name?.pdf` | `filename.pdf` ✅ |
| `.pdf` | `document.pdf` ✅ |
| `report` | `report.pdf` ✅ (auto-adds .pdf) |

## Best Practices

### 1. Always Include Context

```python
# ❌ Bad - Too generic
filename = "document.pdf"

# ✅ Good - Descriptive and unique
filename = "invoice-12345-customer-ABC.pdf"
```

### 2. Use Consistent Naming Patterns

```python
# Invoices
filename = f"invoice-{invoice_id}-{date}.pdf"

# Reports
filename = f"report-{report_type}-{period}.pdf"

# Certificates
filename = f"certificate-{student_id}-{course_code}.pdf"
```

### 3. Include Dates for Sorting

```python
# ✅ Good - Sortable by date
filename = f"2026-01-06-monthly-report.pdf"

# ❌ Less optimal
filename = f"monthly-report-Jan-6-2026.pdf"
```

### 4. Avoid Special Characters

```python
# ✅ Good
filename = "invoice-2024-001.pdf"

# ❌ Problematic (will be sanitized)
filename = "invoice #2024/001!.pdf"  # Becomes "invoice 2024001.pdf"
```

## JavaScript/Node.js Example

```javascript
const axios = require('axios');
const fs = require('fs');

async function generatePDF(html, filename) {
  const response = await axios.post('https://your-domain.com/convert', {
    html: html,
    filename: filename
  }, {
    headers: {
      'X-API-Key': 'YOUR_API_KEY',
      'Content-Type': 'application/json'
    },
    responseType: 'arraybuffer'
  });
  
  fs.writeFileSync(filename, response.data);
  console.log(`PDF saved: ${filename}`);
}

// Usage with dynamic filename
const invoiceId = '12345';
const filename = `invoice-${invoiceId}.pdf`;
await generatePDF('<h1>Invoice</h1>', filename);
```

## PHP Example

```php
<?php

$html = '<h1>Invoice #12345</h1><p>Total: $500</p>';
$filename = 'invoice-12345.pdf';

$data = json_encode([
    'html' => $html,
    'filename' => $filename
]);

$ch = curl_init('https://your-domain.com/convert');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-API-Key: YOUR_API_KEY'
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$pdf = curl_exec($ch);
curl_close($ch);

file_put_contents($filename, $pdf);
echo "PDF saved: $filename\n";
?>
```

## Advanced Use Cases

### Batch Processing with Unique Names

```python
import requests

invoices = [
    {'id': 'INV-001', 'html': '<h1>Invoice 001</h1>'},
    {'id': 'INV-002', 'html': '<h1>Invoice 002</h1>'},
    {'id': 'INV-003', 'html': '<h1>Invoice 003</h1>'}
]

for invoice in invoices:
    response = requests.post(url, json={
        'html': invoice['html'],
        'filename': f"{invoice['id']}.pdf"
    })
    
    with open(f"{invoice['id']}.pdf", 'wb') as f:
        f.write(response.content)
```

### Multi-Language Filenames

```python
# English
filename = "invoice-12345.pdf"

# Spanish
filename = "factura-12345.pdf"

# French
filename = "facture-12345.pdf"

# All work fine with sanitization!
```

## Common Mistakes

### ❌ Mistake 1: Not Including .pdf Extension

```python
# Will be auto-corrected
filename = "invoice-12345"  # Becomes "invoice-12345.pdf"
```

### ❌ Mistake 2: Using Full Paths

```python
# Path components will be removed
filename = "/home/user/invoices/invoice.pdf"  # Becomes "invoice.pdf"
```

### ❌ Mistake 3: Using Same Name for Multiple Files

```python
# This overwrites files!
for invoice in invoices:
    filename = "invoice.pdf"  # All use same name!
    
# Better:
for invoice in invoices:
    filename = f"invoice-{invoice.id}.pdf"  # Unique names
```

## Testing

Test the filename feature:

```bash
# Test basic filename
curl -X POST https://your-domain.com/convert \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"html":"<h1>Test</h1>","filename":"test-123.pdf"}' \
  --output test.pdf

# Check the Content-Disposition header
curl -X POST https://your-domain.com/convert \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"html":"<h1>Test</h1>","filename":"custom-name.pdf"}' \
  -I  # Shows headers including Content-Disposition
```

## Summary

The `filename` parameter:
- ✅ Controls the download filename
- ✅ Automatically sanitized for security
- ✅ Auto-adds `.pdf` extension if missing
- ✅ Defaults to `document.pdf` if not specified
- ✅ Works with all programming languages
- ✅ Perfect for dynamic document generation

---

**See also**: 
- [Main README](../README.md)
- [Usage Examples](../examples/usage_example.py)
- [API Documentation](../README.md#api-documentation)
