# 🚀 Complete Hostinger VPS Deployment Guide

**Deploy Your HTML-to-PDF API on Hostinger VPS with HTTPS in Under 30 Minutes**

This guide walks you through every step of deploying a production-ready Flask API on a Hostinger VPS, from initial server setup to SSL configuration with automatic HTTPS.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial VPS Setup](#step-1-initial-vps-setup)
3. [Domain Configuration](#step-2-domain-configuration)
4. [Server Security Setup](#step-3-server-security-setup)
5. [Install System Dependencies](#step-4-install-system-dependencies)
6. [Deploy Your Application](#step-5-deploy-your-application)
7. [Configure Systemd Service](#step-6-configure-systemd-service)
8. [Setup Nginx Reverse Proxy](#step-7-setup-nginx-reverse-proxy)
9. [Configure SSL/HTTPS](#step-8-configure-ssl-with-lets-encrypt)
10. [Testing & Verification](#step-9-testing--verification)
11. [Maintenance & Updates](#step-10-maintenance--updates)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Hostinger VPS account** (any plan works - even the basic $4.99/month plan)
- ✅ **Domain name** (can be purchased through Hostinger or any domain registrar)
- ✅ **SSH client** (Terminal on Mac/Linux, PuTTY/PowerShell on Windows)
- ✅ **Your project code** on GitHub (or ready to upload)
- ✅ **30 minutes of time** ⏰

### What You'll Get

By the end of this guide:
- 🔐 Secure HTTPS website with auto-renewing SSL certificate
- 🚀 Production-ready API running 24/7
- 🛡️ Protected server with firewall configuration
- 📊 Automatic service restart on failure/reboot
- ⚡ High-performance Gunicorn + Nginx setup

---

## Step 1: Initial VPS Setup

### 1.1 Access Your Hostinger VPS

**Via Hostinger Panel:**

1. Log into your Hostinger account
2. Go to **VPS** section
3. Click on your VPS instance
4. Note your **IP address** and **root password** (or set a new one)

**Connect via SSH:**

```bash
# Replace YOUR_VPS_IP with your actual IP address
ssh root@YOUR_VPS_IP
```

When prompted, enter your root password.

**First Login? You'll see something like:**
```
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-76-generic x86_64)
```

### 1.2 Update System Packages

Always start with system updates:

```bash
# Update package lists
apt-get update

# Upgrade installed packages
apt-get upgrade -y

# Remove unused packages
apt-get autoremove -y
```

**Expected output:**
```
Reading package lists... Done
Building dependency tree... Done
...
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
```

### 1.3 Set System Timezone (Optional but Recommended)

```bash
# Set to your timezone (example: America/New_York)
timedatectl set-timezone America/New_York

# Or use interactive selector
dpkg-reconfigure tzdata
```

---

## Step 2: Domain Configuration

### 2.1 Point Your Domain to VPS

**If domain is with Hostinger:**

1. Go to **Domains** in Hostinger panel
2. Click **Manage** on your domain
3. Go to **DNS / Name Servers**
4. Add/Update these A records:

| Type | Name | Points to | TTL |
|------|------|-----------|-----|
| A | @ | YOUR_VPS_IP | 14400 |
| A | www | YOUR_VPS_IP | 14400 |

**If domain is with another registrar:**

1. Log into your domain registrar
2. Find DNS settings
3. Add A records pointing to your VPS IP address

### 2.2 Verify DNS Propagation

Wait 5-10 minutes, then test:

```bash
# Check if domain resolves to your IP
nslookup yourdomain.com

# Or use dig
dig yourdomain.com +short
```

**Expected output should show your VPS IP:**
```
123.456.789.012
```

---

## Step 3: Server Security Setup

### 3.1 Configure Firewall (UFW)

Ubuntu includes UFW (Uncomplicated Firewall) - let's set it up:

```bash
# Install UFW if not present
apt-get install -y ufw

# Allow SSH (IMPORTANT - do this first!)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

**Expected output:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

### 3.2 Create a Non-Root User (Optional but Recommended)

For better security, create a dedicated user:

```bash
# Create new user
adduser appuser

# Add to sudo group
usermod -aG sudo appuser

# Test the user (optional)
su - appuser
```

**For this guide, we'll continue as root for simplicity.**

### 3.3 Install Fail2Ban (Optional - Protection Against Brute Force)

```bash
# Install fail2ban
apt-get install -y fail2ban

# Start and enable
systemctl start fail2ban
systemctl enable fail2ban

# Check status
systemctl status fail2ban
```

---

## Step 4: Install System Dependencies

### 4.1 Install Python and Build Tools

```bash
# Install Python 3 and development tools
apt-get install -y python3 python3-pip python3-venv python3-dev

# Install build essentials
apt-get install -y build-essential

# Verify installation
python3 --version
pip3 --version
```

**Expected output:**
```
Python 3.10.12
pip 22.0.2
```

### 4.2 Install Application-Specific Dependencies

For the HTML-to-PDF API, we need WeasyPrint dependencies:

```bash
# Install Cairo, Pango, and other libraries
apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info

# Verify installation
pkg-config --modversion cairo
```

### 4.3 Install Web Server and SSL Tools

```bash
# Install Nginx
apt-get install -y nginx

# Install Certbot for SSL
apt-get install -y certbot python3-certbot-nginx

# Start Nginx
systemctl start nginx
systemctl enable nginx

# Verify Nginx is running
systemctl status nginx
```

**Test:** Open `http://YOUR_VPS_IP` in browser - you should see the Nginx welcome page.

### 4.4 Install Git

```bash
# Install Git
apt-get install -y git

# Verify
git --version
```

---

## Step 5: Deploy Your Application

### 5.1 Choose Application Directory

```bash
# Navigate to root directory
cd /root

# Or create a dedicated apps directory
mkdir -p /var/www
cd /var/www
```

**For this guide, we'll use `/root`**

### 5.2 Clone Your Repository

**If your repo is public:**

```bash
cd /root
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

**If your repo is private:**

```bash
# Generate SSH key on VPS
ssh-keygen -t ed25519 -C "your_email@example.com"

# Display public key
cat ~/.ssh/id_ed25519.pub

# Copy the output and add to GitHub:
# GitHub.com → Settings → SSH and GPG keys → New SSH key
```

Then clone:
```bash
git clone git@github.com:YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

**For our HTML-to-PDF example:**
```bash
cd /root
git clone https://github.com/systemifyautomation/HTML-to-PDF.git
cd HTML-to-PDF
```

### 5.3 Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your prompt should now show (venv)
```

### 5.4 Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected output shows all packages:**
```
Flask          3.0.0
WeasyPrint     60.1
gunicorn       21.2.0
...
```

### 5.5 Configure API Keys

```bash
# Copy example file
cp .api-keys.example.json .api-keys.json

# Generate secure keys
python3 -c "import secrets; print('Super User Key:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('API Key 1:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('API Key 2:', secrets.token_urlsafe(32))"

# Edit the file with your keys
nano .api-keys.json
```

**Edit the JSON structure:**
```json
{
  "super_user": {
    "key": "PASTE_YOUR_SUPER_USER_KEY_HERE",
    "name": "Super Admin",
    "created": "2025-12-10",
    "note": "Full admin access"
  },
  "api_keys": [
    {
      "key": "PASTE_YOUR_API_KEY_1_HERE",
      "name": "Production App",
      "created": "2025-12-10",
      "active": true
    },
    {
      "key": "PASTE_YOUR_API_KEY_2_HERE",
      "name": "Mobile App",
      "created": "2025-12-10",
      "active": true
    }
  ],
  "rate_limit": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000
  }
}
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### 5.6 Test Application Manually

```bash
# Make sure venv is activated
source venv/bin/activate

# Test with Flask development server
python3 app.py
```

**Expected output:**
```
INFO:app:API keys loaded successfully. 2 active keys, 0 inactive keys
INFO:__main__:Starting HTML to PDF Converter API on port 5000
 * Running on http://0.0.0.0:5000
```

**Test in another terminal:**
```bash
curl http://localhost:5000/health
```

**Expected response:**
```json
{"status":"healthy","service":"HTML to PDF Converter"}
```

Press `Ctrl+C` to stop the test server.

---

## Step 6: Configure Systemd Service

Systemd will keep your application running 24/7, automatically restart it on crashes, and start it on system reboot.

### 6.1 Create Service File

```bash
nano /etc/systemd/system/htmltopdf.service
```

**Paste this configuration:**

```ini
[Unit]
Description=HTML to PDF Converter API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/HTML-to-PDF
Environment="PATH=/root/HTML-to-PDF/venv/bin"
ExecStart=/root/HTML-to-PDF/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:9001 \
    --timeout 120 \
    --access-logfile /var/log/htmltopdf-access.log \
    --error-logfile /var/log/htmltopdf-error.log \
    --log-level info \
    app:app

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

### 6.2 Understanding the Configuration

| Setting | Purpose |
|---------|---------|
| `--workers 4` | Number of worker processes (adjust based on CPU cores) |
| `--bind 0.0.0.0:9001` | Listen on all interfaces, port 9001 |
| `--timeout 120` | Request timeout (2 minutes for large PDFs) |
| `Restart=always` | Auto-restart on failure |
| `RestartSec=3` | Wait 3 seconds before restart |

**Worker calculation:** `workers = (2 × CPU cores) + 1`

### 6.3 Start and Enable Service

```bash
# Reload systemd to read new service file
systemctl daemon-reload

# Enable service (start on boot)
systemctl enable htmltopdf

# Start service now
systemctl start htmltopdf

# Check status
systemctl status htmltopdf
```

**Expected output:**
```
● htmltopdf.service - HTML to PDF Converter API
     Loaded: loaded (/etc/systemd/system/htmltopdf.service; enabled)
     Active: active (running) since Tue 2025-12-10 10:30:00 UTC; 5s ago
   Main PID: 12345 (gunicorn)
      Tasks: 5 (limit: 2048)
     Memory: 150.0M
```

**Green "active (running)" = Success! ✅**

### 6.4 Test Internal API

```bash
# Test health endpoint
curl http://localhost:9001/health

# Test with your API key
curl -X POST http://localhost:9001/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{"html": "<h1>Test PDF</h1>"}' \
  --output test.pdf

# Check if PDF was created
ls -lh test.pdf
```

### 6.5 View Logs

```bash
# View service logs
journalctl -u htmltopdf -f

# View access logs
tail -f /var/log/htmltopdf-access.log

# View error logs
tail -f /var/log/htmltopdf-error.log
```

Press `Ctrl+C` to stop viewing logs.

---

## Step 7: Setup Nginx Reverse Proxy

Nginx will handle incoming web traffic, SSL/TLS encryption, and proxy requests to your application.

### 7.1 Create Nginx Configuration

```bash
# Create new site configuration
nano /etc/nginx/sites-available/htmltopdf
```

**Paste this configuration:**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Request size limit (for large HTML content)
    client_max_body_size 16M;

    # Proxy settings
    location / {
        proxy_pass http://127.0.0.1:9001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running PDF generation
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Health check endpoint (optional - for monitoring)
    location /health {
        proxy_pass http://127.0.0.1:9001/health;
        access_log off;
    }
}
```

**Replace `yourdomain.com` with your actual domain!**

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

### 7.2 Enable Site Configuration

```bash
# Create symbolic link to enable site
ln -s /etc/nginx/sites-available/htmltopdf /etc/nginx/sites-enabled/

# Remove default site (optional)
rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
```

**Expected output:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 7.3 Reload Nginx

```bash
# Reload Nginx to apply changes
systemctl reload nginx

# Check status
systemctl status nginx
```

### 7.4 Test HTTP Access

```bash
# From VPS
curl http://yourdomain.com/health

# From your computer's browser
# Open: http://yourdomain.com/health
```

**You should see:**
```json
{"status":"healthy","service":"HTML to PDF Converter"}
```

---

## Step 8: Configure SSL with Let's Encrypt

Let's Encrypt provides free SSL certificates that auto-renew.

### 8.1 Run Certbot

```bash
# Run Certbot with Nginx plugin
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**You'll be prompted for:**

1. **Email address:** Enter your email (for renewal notifications)
   ```
   Enter email address: your@email.com
   ```

2. **Terms of Service:** Type `Y` to agree
   ```
   (Y)es/(N)o: Y
   ```

3. **Share email with EFF:** Choose `Y` or `N` (optional)
   ```
   (Y)es/(N)o: N
   ```

4. **Redirect HTTP to HTTPS:** Choose `2` (recommended)
   ```
   1: No redirect
   2: Redirect all requests to HTTPS
   Select: 2
   ```

**Expected output:**
```
Congratulations! You have successfully enabled HTTPS!
```

### 8.2 Verify SSL Certificate

**Check certificate info:**
```bash
certbot certificates
```

**Expected output:**
```
Found the following certs:
  Certificate Name: yourdomain.com
    Domains: yourdomain.com www.yourdomain.com
    Expiry Date: 2026-03-10 (VALID: 89 days)
```

### 8.3 Test Auto-Renewal

```bash
# Dry run (test without actually renewing)
certbot renew --dry-run
```

**Expected output:**
```
Congratulations, all simulated renewals succeeded!
```

### 8.4 Verify HTTPS Configuration

**Nginx config is now automatically updated by Certbot. Check it:**

```bash
cat /etc/nginx/sites-available/htmltopdf
```

**You'll see new SSL configuration blocks added:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ...
}
```

---

## Step 9: Testing & Verification

### 9.1 Test HTTPS Endpoint

**From your browser:**
```
https://yourdomain.com/health
```

**From command line:**
```bash
curl https://yourdomain.com/health
```

### 9.2 Test PDF Generation

```bash
# Test with cURL
curl -X POST https://yourdomain.com/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "html": "<html><body><h1>Hello HTTPS!</h1><p>This is a test PDF from my VPS.</p></body></html>",
    "filename": "test.pdf"
  }' \
  --output test.pdf

# Check file size
ls -lh test.pdf
```

### 9.3 Test Admin API

```bash
# List all API keys
curl -X GET https://yourdomain.com/admin/keys \
  -H "X-Super-User-Key: YOUR_SUPER_USER_KEY"

# Create new API key
curl -X POST https://yourdomain.com/admin/keys \
  -H "Content-Type: application/json" \
  -H "X-Super-User-Key: YOUR_SUPER_USER_KEY" \
  -d '{"name": "Test Client"}'
```

### 9.4 Test Rate Limiting

```bash
# Rapid fire requests to test rate limit
for i in {1..65}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    https://yourdomain.com/health \
    -H "X-API-Key: YOUR_API_KEY"
done
```

**Expected:** First 60 return `200`, rest return `429` (Too Many Requests)

### 9.5 Verify SSL Grade

**Test your SSL configuration:**
- Go to: https://www.ssllabs.com/ssltest/
- Enter your domain
- Wait for scan to complete
- **Goal:** A or A+ rating

### 9.6 Complete Verification Checklist

- [ ] HTTPS loads with green padlock in browser
- [ ] HTTP automatically redirects to HTTPS
- [ ] `/health` endpoint responds
- [ ] PDF generation works with API key
- [ ] Admin API works with super user key
- [ ] Rate limiting is functional
- [ ] Service survives server reboot: `reboot` then check
- [ ] Logs are being written: `tail /var/log/htmltopdf-access.log`

---

## Step 10: Maintenance & Updates

### 10.1 One-Line Update (Recommended)

**From your Windows machine:**

```powershell
# One command updates your VPS
.\update-vps-simple.ps1 -Auto
```

The script automatically:
- ✅ Backs up API keys
- ✅ Uploads updated files
- ✅ Restarts service
- ✅ Verifies deployment
- ✅ Shows version

**First time setup** (SSH keys for passwordless access):

```powershell
# Generate SSH key
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa" -N '""'

# Add to VPS
$pubkey = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"
ssh root@YOUR_VPS_IP "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$pubkey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

See [QUICK_UPDATE_GUIDE.md](QUICK_UPDATE_GUIDE.md) for complete instructions.

### 10.2 Manual Git Update

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Navigate to app directory
cd /opt/html-to-pdf  # Or /root/HTML-to-PDF

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies (if requirements.txt changed)
pip install -r requirements.txt

# Restart service
systemctl restart htmltopdf  # Or html-to-pdf

# Check status
systemctl status htmltopdf
```

### 10.3 View Application Logs

```bash
# Real-time service logs
journalctl -u htmltopdf -f

# Last 100 lines
journalctl -u htmltopdf -n 100

# Access logs
tail -f /var/log/htmltopdf-access.log

# Error logs
tail -f /var/log/htmltopdf-error.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### 10.4 Backup API Keys

```bash
# Backup to local machine
scp root@YOUR_VPS_IP:/opt/html-to-pdf/.api-keys.json ~/backup/

# Or use password manager / encrypted storage
```

### 10.4 System Updates

```bash
# Update system packages monthly
apt-get update
apt-get upgrade -y
apt-get autoremove -y

# Restart services if needed
systemctl restart htmltopdf
systemctl restart nginx
```

### 10.5 Monitor Disk Space

```bash
# Check disk usage
df -h

# Check which directories use most space
du -sh /root/* | sort -h

# Clear old logs if needed
journalctl --vacuum-time=7d
```

### 10.6 SSL Certificate Renewal

**Certificates auto-renew, but verify:**

```bash
# Check expiry
certbot certificates

# Manual renewal (if needed)
certbot renew

# Restart Nginx after renewal
systemctl reload nginx
```

---

## Troubleshooting

### Issue 1: Service Won't Start

**Check logs:**
```bash
journalctl -u htmltopdf -n 50
```

**Common causes:**
- Missing dependencies
- Syntax errors in code
- Port already in use
- Missing `.api-keys.json` file

**Solutions:**
```bash
# Test manually
cd /root/HTML-to-PDF
source venv/bin/activate
python3 app.py

# Check port usage
netstat -tulpn | grep 9001

# Verify file exists
ls -la .api-keys.json
```

### Issue 2: Nginx 502 Bad Gateway

**Cause:** Application not running or wrong port.

**Solution:**
```bash
# Check if app is running
systemctl status htmltopdf

# Test internal connection
curl http://localhost:9001/health

# Restart app
systemctl restart htmltopdf
```

### Issue 3: SSL Certificate Fails

**Common causes:**
- DNS not propagated yet
- Firewall blocking ports 80/443
- Domain doesn't point to VPS

**Solutions:**
```bash
# Verify DNS
nslookup yourdomain.com

# Check firewall
ufw status

# Allow ports
ufw allow 80/tcp
ufw allow 443/tcp

# Try Certbot again
certbot --nginx -d yourdomain.com
```

### Issue 4: PDF Generation Fails

**Check logs:**
```bash
tail -f /var/log/htmltopdf-error.log
```

**Common causes:**
- Missing WeasyPrint dependencies
- Invalid HTML
- Timeout too short

**Solutions:**
```bash
# Reinstall dependencies
apt-get install -y libcairo2 libpango-1.0-0 libgdk-pixbuf-2.0-0

# Increase timeout in service file
nano /etc/systemd/system/htmltopdf.service
# Change: --timeout 120 to --timeout 300

# Reload and restart
systemctl daemon-reload
systemctl restart htmltopdf
```

### Issue 5: High Memory Usage

**Check memory:**
```bash
free -h
top
```

**Reduce workers:**
```bash
nano /etc/systemd/system/htmltopdf.service
# Change: --workers 4 to --workers 2

systemctl daemon-reload
systemctl restart htmltopdf
```

### Issue 6: Permission Denied Errors

**Fix permissions:**
```bash
# Ensure correct ownership
chown -R root:root /root/HTML-to-PDF

# Make scripts executable
chmod +x /root/HTML-to-PDF/*.sh

# Fix log permissions
touch /var/log/htmltopdf-access.log
touch /var/log/htmltopdf-error.log
chown root:root /var/log/htmltopdf-*.log
```

### Issue 7: Port Already in Use

**Find what's using the port:**
```bash
netstat -tulpn | grep 9001
# or
lsof -i :9001
```

**Kill the process:**
```bash
kill -9 PID_NUMBER
```

**Or change port:**
```bash
# In service file
nano /etc/systemd/system/htmltopdf.service
# Change port 9001 to 9002

# In Nginx config
nano /etc/nginx/sites-available/htmltopdf
# Change proxy_pass port to 9002

# Reload both
systemctl daemon-reload
systemctl restart htmltopdf
systemctl reload nginx
```

---

## 🎉 Congratulations!

You've successfully deployed a production-ready Flask API on Hostinger VPS with:

- ✅ HTTPS/SSL encryption
- ✅ Automatic service management
- ✅ Reverse proxy with Nginx
- ✅ Security hardening
- ✅ Auto-renewing SSL certificates
- ✅ Professional logging
- ✅ Rate limiting and authentication

### Next Steps

1. **Set up monitoring:** Use UptimeRobot or Pingdom
2. **Configure backups:** Regular backups of `.api-keys.json`
3. **Add analytics:** Track API usage
4. **Scale up:** Add more workers or upgrade VPS plan
5. **Custom domain:** Add additional domains/subdomains

### Useful Resources

- [Hostinger VPS Documentation](https://www.hostinger.com/tutorials/vps)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/3.0.x/deploying/)

---

**Need Help?**

- Open an issue on GitHub
- Check the troubleshooting section above
- Review application logs for error details
- Contact Hostinger support for VPS issues

---

<div align="center">

**Made with ❤️ for developers deploying on Hostinger VPS**

Happy Deploying! 🚀

</div>
