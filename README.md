# 📄 HTML-to-PDF Converter API

<div align="center">

![Version](https://img.shields.io/badge/Version-2.1.0-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=for-the-badge&logo=flask)
![Playwright](https://img.shields.io/badge/Playwright-PDF_Engine-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Transform HTML to Professional PDFs in Seconds** 🚀

*Production-ready, self-hosted REST API for converting HTML to high-quality PDF documents with browser-like rendering.*

**Perfect for invoices, reports, certificates, and any document automation needs.**

[Quick Start](#-quick-start) • [API Docs](API.md) • [Deploy](DEPLOYMENT.md) • [Update](UPDATING.md)

</div>

---

## 🌟 Why This API?

### 💰 Self-Hosted = Zero Costs
- No per-request fees
- Process unlimited PDFs
- Full control of your infrastructure

### 🔒 Enterprise Security
- API key authentication
- Rate limiting built-in
- Admin controls included
- Your data never leaves your server

### ⚡ Production-Ready
- Browser-like rendering with Playwright
- Fast concurrent processing
- Auto-sized PDFs for perfect layouts
- Full CSS support

### 📦 Easy to Deploy & Update
- One-command deployment (systemd or Docker)
- One-line updates: `.\update-vps-simple.ps1 -Auto`
- Works alongside other services (n8n, Traefik, etc.)

---

## 🚀 Quick Start

### Install Locally

```bash
# Clone repository
git clone https://github.com/yourusername/HTML-to-PDF.git
cd HTML-to-PDF

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Generate API key
python generate_api_key.py add "My First Key"

# Run server
python app.py
```

### Test the API

```bash
curl -X POST http://localhost:5000/convert \
  -H "X-API-Key: your-generated-key" \
  -H "Content-Type: application/json" \
  -d '{"html":"<h1>Hello World!</h1>","filename":"test.pdf"}' \
  --output test.pdf
```

**See [API.md](API.md) for complete endpoint documentation and examples.**

---

## 🎯 Use Cases

### 📄 Invoice Generation
```python
import requests

html = """
<html>
<style>
  body { font-family: Arial; padding: 40px; }
  .total { font-size: 24px; color: #2c5aa0; font-weight: bold; }
</style>
<body>
  <h1>INVOICE #001</h1>
  <p>Date: 2026-01-06</p>
  <p>Customer: John Doe</p>
  <p class="total">Total: $1,234.56</p>
</body>
</html>
"""

response = requests.post(
    "https://your-api.com/convert",
    headers={"X-API-Key": "your-key"},
    json={"html": html, "filename": "invoice-001.pdf"}
)

with open("invoice.pdf", "wb") as f:
    f.write(response.content)
```

### 📊 Dynamic Reports
```javascript
const axios = require('axios');
const fs = require('fs');

const html = `
<html>
<style>
  body { font-family: 'Helvetica'; }
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #ddd; padding: 8px; }
</style>
<body>
  <h1>Sales Report</h1>
  <p>Generated: ${new Date().toLocaleDateString()}</p>
  <table>
    <tr><th>Product</th><th>Sales</th></tr>
    <tr><td>Widget A</td><td>$5,000</td></tr>
    <tr><td>Widget B</td><td>$3,500</td></tr>
  </table>
</body>
</html>
`;

const response = await axios.post(
  'https://your-api.com/convert',
  { html, filename: 'sales-report.pdf', page_size: 'Letter' },
  { headers: { 'X-API-Key': 'your-key' }, responseType: 'arraybuffer' }
);

fs.writeFileSync('report.pdf', response.data);
```

### 🎓 Certificates
```python
def generate_certificate(name, course, date):
    html = f"""
    <html>
    <style>
      body {{
        font-family: 'Georgia', serif;
        text-align: center;
        padding: 100px;
        border: 10px solid gold;
      }}
      h1 {{ font-size: 48px; color: #1a1a1a; }}
      .name {{ font-size: 36px; color: #2c5aa0; margin: 40px 0; }}
    </style>
    <body>
      <h1>🏆 Certificate of Completion</h1>
      <p>This certifies that</p>
      <p class="name">{name}</p>
      <p>has successfully completed</p>
      <p><b>{course}</b></p>
      <p>{date}</p>
    </body>
    </html>
    """
    
    response = requests.post(
        "https://your-api.com/convert",
        headers={"X-API-Key": "your-key"},
        json={
            "html": html,
            "filename": f"certificate-{name.replace(' ', '-')}.pdf",
            "page_size": "Letter",
            "landscape": True
        }
    )
    
    return response.content

# Generate certificate
pdf = generate_certificate("John Doe", "Python 101", "2026-01-06")
```

**More examples in [API.md](API.md)** (Python, JavaScript, PHP, PowerShell, Bash)

---

## 🏗️ Technologies Used

| Technology | Purpose | Why We Use It |
|------------|---------|---------------|
| **Python 3.8+** | Core Runtime | Fast, reliable, great ecosystem |
| **Flask 3.0** | REST API Framework | Lightweight, easy to extend |
| **Playwright** | PDF Rendering | Browser-like rendering, modern web support |
| **Gunicorn** | Production Server | Concurrent requests, worker management |
| **Systemd/Docker** | Deployment | Reliable service management |

### Architecture

```
┌─────────────┐     HTTPS      ┌──────────┐     Port 5000    ┌────────────┐
│   Internet  │ ──────────────► │ Traefik  │ ───────────────► │  Gunicorn  │
└─────────────┘   (SSL/TLS)     └──────────┘   (Reverse Proxy) └────────────┘
                                                                      │
                                                                      ▼
                                                              ┌────────────────┐
                                                              │  Flask App     │
                                                              │  - Auth        │
                                                              │  - Rate Limit  │
                                                              │  - Validation  │
                                                              └────────────────┘
                                                                      │
                                                                      ▼
                                                              ┌────────────────┐
                                                              │  Playwright    │
                                                              │  - Chromium    │
                                                              │  - PDF Engine  │
                                                              └────────────────┘
```

---

## ⚙️ Key Features

### 🔐 Authentication & Security
- **API Key Management**: Generate, activate, deactivate keys
- **Super User Access**: Admin endpoints for key management
- **Rate Limiting**: Configurable per-minute and per-hour limits
- **Input Sanitization**: Automatic filename and parameter validation

### 📄 PDF Generation
- **Custom Filenames**: Dynamic naming with date/time support
- **Page Sizes**: A4, Letter, Legal, A3
- **Margins**: Configurable (inches, cm, px)
- **Orientation**: Portrait or landscape
- **Scale**: Zoom content (0.1 - 2.0)
- **Background Graphics**: Optional printing
- **CSS Page Size**: Respect CSS-defined dimensions

### 🚀 Performance
- **Concurrent Processing**: Multiple workers via Gunicorn
- **Fast Rendering**: Playwright's browser engine
- **Efficient Memory**: Auto-cleanup after generation
- **Rate Limiting**: Prevent abuse, ensure fair usage

### 📊 Monitoring
- **Health Endpoint**: Check API status
- **Version Endpoint**: View current version and changelog
- **Detailed Logging**: Access and error logs
- **Admin Dashboard**: View all API keys and usage

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[API.md](API.md)** | Complete API reference with all endpoints and examples |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Step-by-step deployment guide for VPS |
| **[UPDATING.md](UPDATING.md)** | How to update your VPS with new code |
| **README.md** | This file - project overview |

---

## 🔄 Deployment & Updates

### Deploy to VPS

```bash
# Quick deployment
ssh root@your-vps.com

# Install dependencies, setup service, configure SSL
# See DEPLOYMENT.md for complete guide
```

**Deployment takes ~15 minutes.** Includes:
- Systemd service setup
- SSL/HTTPS configuration
- Integration with existing services (n8n, Traefik)

### Update VPS

```powershell
# One command from your Windows machine
.\update-vps-simple.ps1 -Auto
```

Updates in ~10 seconds with:
- ✅ Automatic API key backup
- ✅ File upload
- ✅ Service restart
- ✅ Verification
- ✅ Zero downtime

**See [DEPLOYMENT.md](DEPLOYMENT.md) and [UPDATING.md](UPDATING.md) for details.**

---

## 🎨 Advantages Over Commercial APIs

| Feature | This API | Commercial APIs |
|---------|----------|-----------------|
| **Cost per PDF** | $0 | $0.001 - $0.01+ |
| **Data Privacy** | 100% on your server | Sent to 3rd party |
| **Customization** | Full source access | Limited |
| **Rate Limits** | Your choice | Strict, paid tiers |
| **Uptime Control** | You manage | Dependent on vendor |
| **Vendor Lock-in** | None | High |

**Cost Comparison:**
- Generate 10,000 PDFs/month
  - **This API**: $0 (after VPS: ~$5/month)
  - **Commercial**: $10 - $100+/month

---

## 🛠️ API Management

### Generate API Keys

```powershell
# Add new key
python generate_api_key.py add "Client Name"

# List all keys
python generate_api_key.py list

# Deactivate key
python generate_api_key.py deactivate <key>

# Reactivate key
python generate_api_key.py activate <key>
```

### Configure Rate Limits

Edit `.api-keys.json`:

```json
{
  "rate_limit": {
    "requests_per_minute": 10,
    "requests_per_hour": 100
  }
}
```

---

## 🧪 Testing

```bash
# Health check
curl https://your-api.com/health

# Version info
curl https://your-api.com/version

# Test conversion
curl -X POST https://your-api.com/convert \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"html":"<h1>Test</h1>","filename":"test.pdf"}' \
  --output test.pdf
```

---

## 📞 Support & Contributing

### Issues
Found a bug? [Open an issue](https://github.com/yourusername/HTML-to-PDF/issues)

### Contributing
Pull requests welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with description

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Playwright](https://playwright.dev/) - Browser automation
- [Gunicorn](https://gunicorn.org/) - WSGI server

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ for the open-source community

</div>
