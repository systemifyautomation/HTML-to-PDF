# API Documentation

Complete API reference for the HTML-to-PDF Converter.

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Version Info](#version-info)
  - [Convert HTML to PDF](#convert-html-to-pdf)
  - [Admin: List API Keys](#admin-list-api-keys)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Code Examples](#code-examples)

---

## Authentication

All endpoints (except `/health` and `/version`) require API key authentication.

**Header:**
```
X-API-Key: your-api-key-here
```

**Managing API Keys:**

```powershell
# Add new API key
python generate_api_key.py add "Client Name"

# List all keys
python generate_api_key.py list

# Deactivate a key
python generate_api_key.py deactivate <key>

# Reactivate a key
python generate_api_key.py activate <key>
```

---

## Endpoints

### Health Check

Check if the API is running.

**Endpoint:** `GET /health`  
**Authentication:** None required

**Example:**

```bash
curl https://htmltopdf.systemifyautomation.com/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-01-06T12:00:00Z"
}
```

---

### Version Info

Get API version and recent changes.

**Endpoint:** `GET /version`  
**Authentication:** None required

**Example:**

```bash
curl https://htmltopdf.systemifyautomation.com/version
```

**Response:**

```json
{
  "version": "2.1.0",
  "updated_at": "2026-01-06T00:00:00Z",
  "changelog": [
    "Enhanced filename parameter with security sanitization",
    "Added comprehensive filename guide and examples",
    "Dynamic filenames support (invoices, reports, dates)",
    "Browser-like PDF rendering with Playwright",
    "Enhanced error handling and validation"
  ]
}
```

---

### Convert HTML to PDF

Convert HTML content to a PDF file.

**Endpoint:** `POST /convert`  
**Authentication:** Required  
**Content-Type:** `application/json`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `html` | string | Yes | HTML content to convert |
| `filename` | string | No | Output filename (default: `document.pdf`) |
| `page_size` | string | No | Page size: `A4`, `Letter`, `Legal`, `A3` (default: `A4`) |
| `margin` | string | No | Page margins: `0.5in`, `1cm`, `20px` (default: `0.4in`) |
| `landscape` | boolean | No | Landscape orientation (default: `false`) |
| `scale` | number | No | Scale factor 0.1-2.0 (default: `1.0`) |
| `print_background` | boolean | No | Print background graphics (default: `true`) |
| `prefer_css_page_size` | boolean | No | Use CSS-defined page size (default: `false`) |

#### Filename Sanitization

The API automatically sanitizes filenames for security:
- Removes path traversal attempts (`../`, `..\\`)
- Strips directory components
- Only allows: letters, numbers, spaces, dots, hyphens, underscores
- Auto-adds `.pdf` extension if missing
- Falls back to `document.pdf` if filename is invalid

#### Examples

**Basic Conversion:**

```bash
curl -X POST https://htmltopdf.systemifyautomation.com/convert \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"html":"<h1>Hello World</h1><p>This is a PDF.</p>"}' \
  --output document.pdf
```

**With Custom Filename:**

```bash
curl -X POST https://htmltopdf.systemifyautomation.com/convert \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "html":"<h1>Invoice</h1><p>Amount: $100</p>",
    "filename":"invoice-2026-01-06.pdf"
  }' \
  --output invoice.pdf
```

**Advanced Options:**

```bash
curl -X POST https://htmltopdf.systemifyautomation.com/convert \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "html":"<h1>Report</h1>",
    "filename":"quarterly-report.pdf",
    "page_size":"Letter",
    "margin":"1in",
    "landscape":true,
    "scale":0.9
  }' \
  --output report.pdf
```

**Response:**

- **Success:** PDF file (binary data)
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `attachment; filename="your-file.pdf"`

---

### Admin: List API Keys

List all API keys (super user only).

**Endpoint:** `GET /admin/keys`  
**Authentication:** Required (super user key only)

**Example:**

```bash
curl https://htmltopdf.systemifyautomation.com/admin/keys \
  -H "X-API-Key: your-super-user-key"
```

**Response:**

```json
{
  "api_keys": [
    {
      "key": "abc...xyz",
      "name": "Client Name",
      "created": "2026-01-06",
      "active": true
    }
  ],
  "total": 1,
  "active": 1,
  "inactive": 0
}
```

---

## Rate Limiting

Default rate limits (configurable in `.api-keys.json`):
- **5 requests per minute**
- **20 requests per hour**

**Rate Limit Headers:**

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1609459200
```

**Rate Limit Exceeded Response:**

```json
{
  "error": "Rate limit exceeded. Try again in X seconds."
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error description",
  "details": "Additional information (if available)"
}
```

### Common Errors

| Status Code | Error | Cause |
|-------------|-------|-------|
| `400` | Missing HTML content | No `html` parameter in request |
| `401` | Missing API key | No `X-API-Key` header |
| `401` | Invalid API key | Key not found or inactive |
| `403` | Rate limit exceeded | Too many requests |
| `500` | PDF generation failed | Server error during conversion |

---

## Code Examples

### Python

```python
import requests
from datetime import datetime

API_URL = "https://htmltopdf.systemifyautomation.com/convert"
API_KEY = "your-api-key"

# Simple conversion
html = "<h1>Hello World</h1><p>Generated by Python</p>"
response = requests.post(
    API_URL,
    headers={"X-API-Key": API_KEY},
    json={"html": html, "filename": "python-example.pdf"}
)

with open("output.pdf", "wb") as f:
    f.write(response.content)

# Dynamic invoice with date
invoice_html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial; padding: 20px; }}
        .header {{ text-align: center; color: #333; }}
        .amount {{ font-size: 24px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1 class="header">Invoice</h1>
    <p>Date: {datetime.now().strftime('%Y-%m-%d')}</p>
    <p class="amount">Total: $1,234.56</p>
</body>
</html>
"""

response = requests.post(
    API_URL,
    headers={"X-API-Key": API_KEY},
    json={
        "html": invoice_html,
        "filename": f"invoice-{datetime.now().strftime('%Y%m%d')}.pdf",
        "page_size": "Letter",
        "margin": "1in"
    }
)

with open("invoice.pdf", "wb") as f:
    f.write(response.content)

print(f"Invoice saved! Size: {len(response.content)} bytes")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');
const fs = require('fs');

const API_URL = 'https://htmltopdf.systemifyautomation.com/convert';
const API_KEY = 'your-api-key';

async function convertToPdf() {
  const html = `
    <h1>Hello from JavaScript</h1>
    <p>Date: ${new Date().toLocaleDateString()}</p>
  `;

  try {
    const response = await axios.post(
      API_URL,
      {
        html: html,
        filename: 'javascript-example.pdf',
        page_size: 'A4'
      },
      {
        headers: { 'X-API-Key': API_KEY },
        responseType: 'arraybuffer'
      }
    );

    fs.writeFileSync('output.pdf', response.data);
    console.log('PDF created successfully!');
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

convertToPdf();
```

### PHP

```php
<?php
$apiUrl = 'https://htmltopdf.systemifyautomation.com/convert';
$apiKey = 'your-api-key';

$html = '<h1>Hello from PHP</h1><p>Generated on ' . date('Y-m-d') . '</p>';

$data = [
    'html' => $html,
    'filename' => 'php-example.pdf',
    'page_size' => 'A4'
];

$options = [
    'http' => [
        'header'  => [
            'Content-Type: application/json',
            'X-API-Key: ' . $apiKey
        ],
        'method'  => 'POST',
        'content' => json_encode($data)
    ]
];

$context = stream_context_create($options);
$result = file_get_contents($apiUrl, false, $context);

if ($result !== false) {
    file_put_contents('output.pdf', $result);
    echo "PDF created successfully!";
} else {
    echo "Error creating PDF";
}
?>
```

### cURL (Bash)

```bash
#!/bin/bash

API_URL="https://htmltopdf.systemifyautomation.com/convert"
API_KEY="your-api-key"
DATE=$(date +%Y-%m-%d)

# Create HTML with current date
HTML="<h1>Report</h1><p>Generated: $DATE</p>"

# Convert to PDF
curl -X POST "$API_URL" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"html\":\"$HTML\",
    \"filename\":\"report-$DATE.pdf\",
    \"page_size\":\"Letter\"
  }" \
  --output "report-$DATE.pdf"

echo "PDF created: report-$DATE.pdf"
```

### PowerShell

```powershell
$apiUrl = "https://htmltopdf.systemifyautomation.com/convert"
$apiKey = "your-api-key"
$date = Get-Date -Format "yyyy-MM-dd"

$html = "<h1>PowerShell Report</h1><p>Date: $date</p>"

$body = @{
    html = $html
    filename = "report-$date.pdf"
    page_size = "Letter"
} | ConvertTo-Json

$headers = @{
    "X-API-Key" = $apiKey
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $body -OutFile "report.pdf"

Write-Host "PDF created successfully!"
```

---

## Advanced Use Cases

### Invoice Generation

```python
def generate_invoice(invoice_data):
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica', sans-serif; padding: 40px; }}
            .header {{ border-bottom: 2px solid #333; padding-bottom: 20px; }}
            .invoice-details {{ margin: 30px 0; }}
            .total {{ font-size: 24px; font-weight: bold; color: #2c5aa0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>INVOICE</h1>
            <p>Invoice #: {invoice_data['number']}</p>
            <p>Date: {invoice_data['date']}</p>
        </div>
        <div class="invoice-details">
            <h3>Bill To:</h3>
            <p>{invoice_data['customer_name']}</p>
            <p>{invoice_data['customer_email']}</p>
        </div>
        <div class="total">
            Total: ${invoice_data['amount']}
        </div>
    </body>
    </html>
    """
    
    response = requests.post(
        API_URL,
        headers={"X-API-Key": API_KEY},
        json={
            "html": html,
            "filename": f"invoice-{invoice_data['number']}.pdf",
            "page_size": "Letter"
        }
    )
    
    return response.content

# Usage
invoice = generate_invoice({
    "number": "INV-001",
    "date": "2026-01-06",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "amount": "1,234.56"
})
```

### Batch Processing

```python
def batch_convert(html_files):
    """Convert multiple HTML files to PDFs"""
    results = []
    
    for html_file in html_files:
        with open(html_file, 'r') as f:
            html = f.read()
        
        filename = html_file.replace('.html', '.pdf')
        
        response = requests.post(
            API_URL,
            headers={"X-API-Key": API_KEY},
            json={"html": html, "filename": filename}
        )
        
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            results.append({"file": filename, "status": "success"})
        else:
            results.append({"file": filename, "status": "failed"})
    
    return results
```

---

## Tips & Best Practices

### Performance

- **Minimize HTML size**: Large HTML files take longer to process
- **Optimize images**: Use compressed images or external URLs
- **Use CSS efficiently**: Inline critical CSS, external for large stylesheets

### Security

- **Never expose your API key** in client-side code
- **Validate HTML** before sending to avoid errors
- **Sanitize user input** if accepting HTML from users

### Reliability

- **Implement retry logic** for network errors
- **Handle rate limits** gracefully
- **Cache generated PDFs** when possible to reduce API calls

### Troubleshooting

**PDF generation fails:**
- Check HTML syntax validity
- Ensure all external resources are accessible
- Verify CSS doesn't break rendering

**Rate limit errors:**
- Implement exponential backoff
- Consider caching frequently generated PDFs
- Contact admin to increase limits if needed

---

For deployment and setup instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).  
For updating your VPS, see [UPDATING.md](UPDATING.md).
