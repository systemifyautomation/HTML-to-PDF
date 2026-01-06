# 🚀 Deploy HTML-to-PDF on systemifyautomation.com VPS

**Quick deployment guide for htmltopdf.systemifyautomation.com alongside n8n.systemifyautomation.com**

---

## 📋 Current Setup

- **n8n**: Running at `n8n.systemifyautomation.com`
- **New Service**: HTML-to-PDF API at `htmltopdf.systemifyautomation.com`
- **Server**: Hostinger VPS

---

## 🎯 Architecture

```
Internet
    ↓
Nginx (Port 80/443)
    ├─→ n8n.systemifyautomation.com → n8n service
    └─→ htmltopdf.systemifyautomation.com → HTML-to-PDF API (port 5000)
```

---

## Step 1: Configure DNS (In Hostinger Control Panel)

### 1.1 Add DNS Record

1. Log in to Hostinger Control Panel
2. Go to **Domains** → **DNS / Name Servers**
3. Add new **A Record**:
   - **Type**: A
   - **Name**: `htmltopdf`
   - **Points to**: Your VPS IP address
   - **TTL**: 14400 (or default)

4. Save and wait 5-10 minutes for DNS propagation

### 1.2 Verify DNS

From your local machine:

```powershell
# Check if DNS is propagated
nslookup htmltopdf.systemifyautomation.com
```

Should return your VPS IP address.

---

## Step 2: Deploy Using Automated Script

### 2.1 Run Deployment Script

From your local machine (PowerShell):

```powershell
cd C:\Users\PCZZ3\Documents\GitHub\HTML-to-PDF

# Run the deployment script
.\deploy-to-vps.ps1 -VPS_USER "your-vps-username" -VPS_HOST "htmltopdf.systemifyautomation.com"
```

**What the script does**:
- ✓ Uploads all application files
- ✓ Creates `/opt/html-to-pdf` directory
- ✓ Installs Python dependencies
- ✓ Installs Playwright + Chromium
- ✓ Creates systemd service
- ✓ Starts the application on port 5000

### 2.2 Upload API Keys

If the script didn't upload your API keys:

```powershell
scp .api-keys.json your-username@htmltopdf.systemifyautomation.com:/opt/html-to-pdf/.api-keys.json
```

---

## Step 3: Configure Nginx

### 3.1 Upload Nginx Configuration

From your local machine:

```powershell
scp deployment\nginx-htmltopdf.conf your-username@htmltopdf.systemifyautomation.com:/tmp/htmltopdf.conf
```

### 3.2 Install Configuration on VPS

SSH into your VPS:

```powershell
ssh your-username@htmltopdf.systemifyautomation.com
```

Then run:

```bash
# Copy configuration to nginx sites-available
sudo cp /tmp/htmltopdf.conf /etc/nginx/sites-available/htmltopdf.conf

# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/htmltopdf.conf /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

---

## Step 4: Set Up SSL/HTTPS

### 4.1 Install Certbot (if not already installed)

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### 4.2 Obtain SSL Certificate

```bash
sudo certbot --nginx -d htmltopdf.systemifyautomation.com
```

Follow the prompts:
- Enter your email address
- Agree to terms of service
- Choose option 2: Redirect HTTP to HTTPS (recommended)

Certbot will automatically:
- Obtain SSL certificate
- Update nginx configuration
- Set up auto-renewal

### 4.3 Verify Auto-Renewal

```bash
sudo certbot renew --dry-run
```

---

## Step 5: Test Your Deployment

### 5.1 Test Health Endpoint

From your local machine:

```powershell
# Test HTTP (should redirect to HTTPS)
curl http://htmltopdf.systemifyautomation.com/health

# Test HTTPS
curl https://htmltopdf.systemifyautomation.com/health
```

Expected response:
```json
{"status":"healthy"}
```

### 5.2 Test PDF Conversion

Create a test script `test-production.ps1`:

```powershell
# Test PDF conversion on production
$apiKey = "your-production-api-key"

$body = @{
    html = @"
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        .info { background: #ecf0f1; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Production Test - systemifyautomation.com</h1>
    <div class="info">
        <p><strong>Service:</strong> HTML-to-PDF Converter</p>
        <p><strong>Endpoint:</strong> htmltopdf.systemifyautomation.com</p>
        <p><strong>Status:</strong> ✓ Running</p>
        <p><strong>Generated:</strong> $(Get-Date)</p>
    </div>
</body>
</html>
"@
    options = @{
        format = "A4"
        margin = @{
            top = "1cm"
            right = "1cm"
            bottom = "1cm"
            left = "1cm"
        }
    }
} | ConvertTo-Json -Depth 10

$headers = @{
    "X-API-Key" = $apiKey
    "Content-Type" = "application/json"
}

Invoke-RestMethod `
    -Uri "https://htmltopdf.systemifyautomation.com/convert" `
    -Method POST `
    -Headers $headers `
    -Body $body `
    -OutFile "production-test.pdf"

Write-Host "✓ PDF generated successfully: production-test.pdf" -ForegroundColor Green
```

Run it:

```powershell
.\test-production.ps1
```

Check if `production-test.pdf` was created!

---

## Step 6: Integrate with n8n

### 6.1 Create n8n Workflow

1. Open n8n at `https://n8n.systemifyautomation.com`
2. Create a new workflow
3. Add **HTTP Request** node

### 6.2 Configure HTTP Request Node

**Settings**:
- **Method**: POST
- **URL**: `https://htmltopdf.systemifyautomation.com/convert`
- **Authentication**: None (we use header)

**Headers**:
```json
{
  "X-API-Key": "your-n8n-integration-key",
  "Content-Type": "application/json"
}
```

**Body**:
```json
{
  "html": "={{ $json.htmlContent }}",
  "options": {
    "format": "A4",
    "margin": {
      "top": "1cm",
      "right": "1cm",
      "bottom": "1cm",
      "left": "1cm"
    }
  }
}
```

**Response Format**: File

### 6.3 Example n8n Workflow

```
Webhook (Trigger)
    ↓
Code Node (Generate HTML)
    ↓
HTTP Request (Convert to PDF)
    ↓
Send Email (Attach PDF)
```

---

## 📊 Monitoring & Maintenance

### Check Service Status

```bash
# SSH into VPS
ssh your-username@htmltopdf.systemifyautomation.com

# Check service status
sudo systemctl status html-to-pdf

# View live logs
sudo journalctl -u html-to-pdf -f

# Check application logs
sudo tail -f /var/log/html-to-pdf-error.log
```

### Check Nginx Status

```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# View access logs
sudo tail -f /var/log/nginx/htmltopdf_access.log

# View error logs
sudo tail -f /var/log/nginx/htmltopdf_error.log
```

### Restart Service

```bash
sudo systemctl restart html-to-pdf
```

---

## 🔄 Update Application

### Method 1: Using Git (Recommended)

```bash
# SSH into VPS
ssh your-username@htmltopdf.systemifyautomation.com

# Update code
cd /opt/html-to-pdf
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart html-to-pdf
```

### Method 2: Full Redeployment

From your local machine:

```powershell
.\deploy-to-vps.ps1 -VPS_USER "your-username" -VPS_HOST "htmltopdf.systemifyautomation.com"
```

---

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check detailed logs
sudo journalctl -u html-to-pdf -n 100 --no-pager

# Test manually
cd /opt/html-to-pdf
source venv/bin/activate
python app.py
```

### DNS Not Resolving

```powershell
# From local machine, check DNS
nslookup htmltopdf.systemifyautomation.com

# Check if it points to correct IP
ping htmltopdf.systemifyautomation.com
```

### SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal
```

### 502 Bad Gateway

This usually means the Flask app isn't running:

```bash
# Check if service is running
sudo systemctl status html-to-pdf

# Check if port 5000 is listening
sudo netstat -tlnp | grep 5000

# Restart service
sudo systemctl restart html-to-pdf
```

### 413 Request Entity Too Large

Increase nginx upload limit:

```bash
sudo nano /etc/nginx/sites-available/htmltopdf.conf

# Increase client_max_body_size (e.g., to 32M)
# Then reload nginx
sudo systemctl reload nginx
```

---

## 📝 Configuration Files Reference

### Systemd Service
**Location**: `/etc/systemd/system/html-to-pdf.service`

```ini
[Unit]
Description=HTML-to-PDF Converter API
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/html-to-pdf
Environment="PATH=/opt/html-to-pdf/venv/bin"
ExecStart=/opt/html-to-pdf/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --timeout 120 --access-logfile /var/log/html-to-pdf-access.log --error-logfile /var/log/html-to-pdf-error.log app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
**Location**: `/etc/nginx/sites-available/htmltopdf.conf`

See [deployment/nginx-htmltopdf.conf](deployment/nginx-htmltopdf.conf)

### Environment Variables
**Location**: `/opt/html-to-pdf/.env`

```env
FLASK_ENV=production
PORT=5000
HOST=127.0.0.1
MAX_CONTENT_LENGTH=16777216
LOG_LEVEL=INFO
```

---

## 📱 Quick Commands Cheat Sheet

```bash
# Service management
sudo systemctl start html-to-pdf
sudo systemctl stop html-to-pdf
sudo systemctl restart html-to-pdf
sudo systemctl status html-to-pdf

# View logs
sudo journalctl -u html-to-pdf -f
sudo tail -f /var/log/html-to-pdf-error.log
sudo tail -f /var/log/nginx/htmltopdf_error.log

# Nginx management
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart nginx

# Test endpoints
curl https://htmltopdf.systemifyautomation.com/health
curl https://htmltopdf.systemifyautomation.com/api-info

# SSL certificate
sudo certbot certificates
sudo certbot renew
```

---

## ✅ Deployment Checklist

- [ ] DNS record created for htmltopdf.systemifyautomation.com
- [ ] DNS propagated (nslookup shows correct IP)
- [ ] Application deployed to /opt/html-to-pdf
- [ ] Python dependencies installed
- [ ] Playwright Chromium installed
- [ ] Production API keys configured
- [ ] Systemd service created and running
- [ ] Nginx configuration installed and enabled
- [ ] Nginx test passed (sudo nginx -t)
- [ ] SSL certificate obtained
- [ ] HTTPS redirect working
- [ ] Health endpoint returns {"status":"healthy"}
- [ ] PDF conversion tested successfully
- [ ] n8n integration tested and working

---

## 🎉 You're Live!

Your HTML-to-PDF API is now running at:

**🔗 Endpoints**:
- Health: `https://htmltopdf.systemifyautomation.com/health`
- Convert: `https://htmltopdf.systemifyautomation.com/convert`
- API Info: `https://htmltopdf.systemifyautomation.com/api-info`

**📊 Monitoring**:
- Logs: `/var/log/html-to-pdf-*.log`
- Service: `sudo systemctl status html-to-pdf`

**🔄 Updates**:
- Pull latest: `cd /opt/html-to-pdf && git pull`
- Restart: `sudo systemctl restart html-to-pdf`

---

**Need Help?** Check the logs first, then review the troubleshooting section above.
