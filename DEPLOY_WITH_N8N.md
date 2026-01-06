# 🚀 Deploy HTML-to-PDF API on Hostinger VPS (Alongside n8n)

**Complete A-Z guide for deploying your HTML-to-PDF API on a Hostinger VPS where n8n is already running on port 80.**

---

## 📋 Current Setup

- **n8n**: Running on port 80 (likely with nginx reverse proxy)
- **New Service**: HTML-to-PDF API (will run on port 5000 internally)
- **Access**: Via reverse proxy at `/api/pdf/*` or subdomain

---

## 🎯 Deployment Overview

```
Internet
    ↓
Nginx (Port 80/443)
    ├─→ / (n8n on port 5173 or similar)
    └─→ /api/pdf/* (HTML-to-PDF on port 5000)
```

---

## Step 1: Prepare Your Local Machine

### 1.1 Generate Production API Keys

On your local machine:

```powershell
# Generate a super user API key
python generate_api_key.py
```

**Save the generated key securely** - you'll need it later!

### 1.2 Create Production API Keys File

Create `.api-keys.json` with your production keys:

```json
{
  "super_user_key_here": {
    "name": "Production Super User",
    "level": "super_user",
    "rate_limits": {
      "requests_per_minute": 100,
      "requests_per_hour": 5000
    },
    "active": true,
    "created_at": "2026-01-06T00:00:00Z"
  },
  "n8n_integration_key_here": {
    "name": "n8n Workflows",
    "level": "standard",
    "rate_limits": {
      "requests_per_minute": 30,
      "requests_per_hour": 1000
    },
    "active": true,
    "created_at": "2026-01-06T00:00:00Z"
  }
}
```

---

## Step 2: Connect to Your VPS

```powershell
# Replace with your actual VPS credentials
ssh username@your-vps-ip

# Or if you have a domain configured:
ssh username@yourdomain.com
```

---

## Step 3: Install System Dependencies

### 3.1 Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 3.2 Install Python and Required Libraries

```bash
# Install Python 3.11+ and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Playwright system dependencies
sudo apt install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libxshmfence1 libpango-1.0-0 \
    libcairo2 fonts-liberation libappindicator3-1
```

### 3.3 Verify Installations

```bash
python3 --version  # Should show Python 3.8+
pip3 --version
```

---

## Step 4: Deploy Your Application

### 4.1 Create Application Directory

```bash
# Create directory for the app
sudo mkdir -p /opt/html-to-pdf
sudo chown $USER:$USER /opt/html-to-pdf
cd /opt/html-to-pdf
```

### 4.2 Clone Your Repository

```bash
# Clone from GitHub (replace with your repo URL)
git clone https://github.com/YOUR-USERNAME/HTML-to-PDF.git .

# Or upload files manually using SCP from your local machine:
# scp -r C:\Users\PCZZ3\Documents\GitHub\HTML-to-PDF/* username@your-vps:/opt/html-to-pdf/
```

### 4.3 Set Up Python Virtual Environment

```bash
cd /opt/html-to-pdf

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Playwright and Chromium browser
playwright install chromium
```

### 4.4 Upload Production API Keys

From your **local machine**, upload the `.api-keys.json` file:

```powershell
# From your local machine (PowerShell)
scp C:\Users\PCZZ3\Documents\GitHub\HTML-to-PDF\.api-keys.json username@your-vps:/opt/html-to-pdf/.api-keys.json
```

Or create it directly on the VPS:

```bash
nano /opt/html-to-pdf/.api-keys.json
# Paste your production API keys, save with Ctrl+O, exit with Ctrl+X
```

### 4.5 Create Environment File

```bash
nano /opt/html-to-pdf/.env
```

Add:

```env
FLASK_ENV=production
PORT=5000
HOST=127.0.0.1
MAX_CONTENT_LENGTH=16777216
LOG_LEVEL=INFO
```

Save with `Ctrl+O`, exit with `Ctrl+X`.

### 4.6 Test the Application

```bash
# Make sure virtual environment is activated
source /opt/html-to-pdf/venv/bin/activate

# Test run
python app.py
```

In another SSH session, test:

```bash
curl http://localhost:5000/health
```

If you see `{"status": "healthy"}`, press `Ctrl+C` to stop the test.

---

## Step 5: Configure Systemd Service

### 5.1 Create Service File

```bash
sudo nano /etc/systemd/system/html-to-pdf.service
```

Add this content:

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

**Important**: Replace `your-username` with your actual VPS username.

### 5.2 Create Log Files

```bash
sudo touch /var/log/html-to-pdf-access.log
sudo touch /var/log/html-to-pdf-error.log
sudo chown $USER:$USER /var/log/html-to-pdf-*.log
```

### 5.3 Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable html-to-pdf

# Start the service
sudo systemctl start html-to-pdf

# Check status
sudo systemctl status html-to-pdf
```

You should see `Active: active (running)` in green.

### 5.4 Verify Service is Running

```bash
# Check if service is listening on port 5000
sudo netstat -tlnp | grep 5000

# Test the endpoint
curl http://127.0.0.1:5000/health
```

---

## Step 6: Configure Nginx (Alongside n8n)

### 6.1 Backup Existing Nginx Configuration

```bash
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
```

### 6.2 Check Current n8n Configuration

```bash
# View current nginx configuration
sudo cat /etc/nginx/sites-available/default
```

### 6.3 Update Nginx Configuration

Since n8n is running on port 80, we need to add a new location block for the HTML-to-PDF API.

```bash
sudo nano /etc/nginx/sites-available/default
```

**Option A: Add as API Endpoint Path** (Recommended)

Add this location block to your existing server configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;  # Your existing domain
    
    # Existing n8n configuration (keep as is)
    location / {
        proxy_pass http://localhost:5173;  # or wherever n8n runs
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # NEW: HTML-to-PDF API
    location /api/pdf {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Upload size limit (16MB for PDF generation)
        client_max_body_size 16M;
        
        # Timeouts for PDF generation
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

**Option B: Create Subdomain** (If you prefer `pdf.yourdomain.com`)

Create a new server block:

```nginx
# Add this as a new server block
server {
    listen 80;
    server_name pdf.yourdomain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        client_max_body_size 16M;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### 6.4 Test and Reload Nginx

```bash
# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

---

## Step 7: Configure Firewall (If Enabled)

```bash
# Check if firewall is active
sudo ufw status

# If active, ensure ports 80 and 443 are allowed
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

---

## Step 8: Test Your Deployment

### 8.1 Test Health Endpoint

```bash
# From VPS
curl http://localhost/api/pdf/health

# From your local machine
curl http://yourdomain.com/api/pdf/health
```

Expected response:
```json
{"status": "healthy"}
```

### 8.2 Test PDF Conversion

From your local machine (PowerShell):

```powershell
# Create test payload
$body = @{
    html = "<html><body><h1>Test PDF</h1><p>Generated from VPS!</p></body></html>"
} | ConvertTo-Json

# Send request (replace with your actual API key)
$headers = @{
    "X-API-Key" = "your-production-api-key-here"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://yourdomain.com/api/pdf/convert" -Method POST -Headers $headers -Body $body -OutFile "test-from-vps.pdf"
```

Check if `test-from-vps.pdf` was created successfully!

---

## Step 9: Set Up SSL/HTTPS (Recommended)

### 9.1 Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 9.2 Obtain SSL Certificate

```bash
# For main domain with path (/api/pdf)
sudo certbot --nginx -d yourdomain.com

# Or for subdomain (pdf.yourdomain.com)
sudo certbot --nginx -d pdf.yourdomain.com
```

Follow the prompts:
- Enter your email
- Agree to terms
- Choose redirect option (recommended: redirect HTTP to HTTPS)

### 9.3 Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

Now your API is accessible via HTTPS! 🎉

---

## Step 10: Integrate with n8n

### 10.1 In n8n, Create HTTP Request Node

1. Add **HTTP Request** node
2. Configure:
   - **Method**: POST
   - **URL**: `https://yourdomain.com/api/pdf/convert`
   - **Authentication**: None (we use header)
   - **Headers**:
     - Name: `X-API-Key`
     - Value: `your-n8n-integration-key`
   - **Body**:
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

### 10.2 Handle Response

- Response will be binary PDF data
- Use **Write Binary File** node or **Send Email** node to use the PDF

---

## 📊 Monitoring & Maintenance

### Check Service Status

```bash
# Check if service is running
sudo systemctl status html-to-pdf

# View recent logs
sudo journalctl -u html-to-pdf -n 50 --no-pager

# Follow live logs
sudo journalctl -u html-to-pdf -f
```

### Check Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### Application Logs

```bash
# Access logs
sudo tail -f /var/log/html-to-pdf-access.log

# Error logs
sudo tail -f /var/log/html-to-pdf-error.log
```

### Restart Service

```bash
sudo systemctl restart html-to-pdf
```

---

## 🔄 Update Application

### Method 1: Using Git

```bash
cd /opt/html-to-pdf
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart html-to-pdf
```

### Method 2: Using Update Script

From your local machine:

```powershell
# Use the provided update script
.\update-vps.ps1
```

---

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check detailed error logs
sudo journalctl -u html-to-pdf -n 100 --no-pager

# Check if port 5000 is already in use
sudo netstat -tlnp | grep 5000

# Test app manually
cd /opt/html-to-pdf
source venv/bin/activate
python app.py
```

### Playwright Browser Issues

```bash
# Reinstall browsers
cd /opt/html-to-pdf
source venv/bin/activate
playwright install chromium
playwright install-deps chromium
```

### Nginx Issues

```bash
# Test configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# Restart nginx
sudo systemctl restart nginx
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/html-to-pdf

# Fix log permissions
sudo chown $USER:$USER /var/log/html-to-pdf-*.log
```

### PDF Generation Fails

```bash
# Check if Chromium is installed
cd /opt/html-to-pdf
source venv/bin/activate
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); print('Chromium OK'); browser.close(); p.stop()"
```

---

## 📝 Quick Reference

### Key Files and Locations

| File/Directory | Location |
|----------------|----------|
| Application | `/opt/html-to-pdf/` |
| Virtual Environment | `/opt/html-to-pdf/venv/` |
| API Keys | `/opt/html-to-pdf/.api-keys.json` |
| Environment | `/opt/html-to-pdf/.env` |
| Systemd Service | `/etc/systemd/system/html-to-pdf.service` |
| Nginx Config | `/etc/nginx/sites-available/default` |
| Access Logs | `/var/log/html-to-pdf-access.log` |
| Error Logs | `/var/log/html-to-pdf-error.log` |

### Common Commands

```bash
# Service management
sudo systemctl start html-to-pdf
sudo systemctl stop html-to-pdf
sudo systemctl restart html-to-pdf
sudo systemctl status html-to-pdf

# View logs
sudo journalctl -u html-to-pdf -f
sudo tail -f /var/log/html-to-pdf-error.log

# Test endpoints
curl http://localhost:5000/health
curl http://yourdomain.com/api/pdf/health

# Nginx management
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart nginx
```

---

## ✅ Deployment Checklist

- [ ] VPS access configured
- [ ] System dependencies installed
- [ ] Application deployed to `/opt/html-to-pdf`
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright Chromium installed
- [ ] Production API keys configured
- [ ] Environment file created
- [ ] Systemd service created and enabled
- [ ] Service running (`systemctl status html-to-pdf`)
- [ ] Nginx configured (path or subdomain)
- [ ] Nginx reloaded successfully
- [ ] Health endpoint accessible
- [ ] PDF conversion tested
- [ ] SSL/HTTPS configured (optional but recommended)
- [ ] n8n integration tested

---

## 🎉 Success!

Your HTML-to-PDF API is now running in production alongside n8n!

**Access your API at**:
- Health: `https://yourdomain.com/api/pdf/health`
- Convert: `https://yourdomain.com/api/pdf/convert`

**Next Steps**:
1. Set up monitoring (uptime checks, error alerts)
2. Configure backups for `/opt/html-to-pdf/`
3. Document your API keys in a password manager
4. Create automated update scripts
5. Set up log rotation

---

**Need Help?** Check the troubleshooting section or review logs for detailed error messages.
