# Deployment Guide

Complete guide to deploying HTML-to-PDF Converter API on your VPS.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Deployment](#quick-deployment)
- [Detailed Setup](#detailed-setup)
- [SSL/HTTPS Configuration](#ssl-https-configuration)
- [Verify Deployment](#verify-deployment)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need

- **VPS**: Any Linux VPS (Ubuntu 20.04+ recommended)
  - Minimum: 1GB RAM, 1 CPU
  - Recommended: 2GB RAM, 2 CPU
- **Domain**: Pointed to your VPS IP
- **SSH Access**: Root or sudo user
- **20 minutes**: For complete setup

### Supported Platforms

✅ Ubuntu 20.04 / 22.04 / 24.04  
✅ Debian 10 / 11 / 12  
✅ CentOS 8+ / Rocky Linux  
✅ Any systemd-based Linux

---

## Quick Deployment

### Step 1: Connect to VPS

```bash
ssh root@your-domain.com
```

### Step 2: Install Dependencies

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Python and system dependencies
apt-get install -y python3 python3-pip python3-venv git \
  libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libasound2t64 \
  libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxfixes3 \
  fonts-liberation fonts-noto-color-emoji
```

### Step 3: Create Installation Directory

```bash
mkdir -p /opt/html-to-pdf
cd /opt/html-to-pdf
```

### Step 4: Setup Application

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install Flask==3.0.0 gunicorn==22.0.0 playwright==1.40.0

# Install Playwright browser
playwright install chromium
```

### Step 5: Upload Your Code

**From your local machine:**

```powershell
# Upload main files
scp app.py version.json requirements.txt root@your-domain.com:/opt/html-to-pdf/

# Upload key generator
scp generate_api_key.py root@your-domain.com:/opt/html-to-pdf/
```

### Step 6: Generate API Keys

```bash
# SSH into VPS
ssh root@your-domain.com

cd /opt/html-to-pdf
source venv/bin/activate

# Generate your first API key
python generate_api_key.py add "Production Key"
```

### Step 7: Create Systemd Service

Create `/etc/systemd/system/html-to-pdf.service`:

```ini
[Unit]
Description=HTML-to-PDF Converter API
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/opt/html-to-pdf
Environment="PATH=/opt/html-to-pdf/venv/bin"
ExecStart=/opt/html-to-pdf/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile /var/log/html-to-pdf-access.log \
    --error-logfile /var/log/html-to-pdf-error.log \
    app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Step 8: Start Service

```bash
# Reload systemd
systemctl daemon-reload

# Enable and start service
systemctl enable html-to-pdf
systemctl start html-to-pdf

# Check status
systemctl status html-to-pdf
```

---

## SSL/HTTPS Configuration

### Option 1: With Existing Traefik

If you already have Traefik running (e.g., for n8n):

**Create nginx proxy container:**

```bash
cd /opt/html-to-pdf
mkdir -p traefik-proxy
cd traefik-proxy
```

**Create `Dockerfile`:**

```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Create `nginx.conf`:**

```nginx
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        
        location / {
            proxy_pass http://host.docker.internal:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

**Create `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  htmltopdf-proxy:
    build: .
    container_name: htmltopdf-proxy
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - traefik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.htmltopdf.rule=Host(`htmltopdf.your-domain.com`)"
      - "traefik.http.routers.htmltopdf.entrypoints=websecure"
      - "traefik.http.routers.htmltopdf.tls.certresolver=mytlschallenge"
      - "traefik.http.services.htmltopdf.loadbalancer.server.port=80"

networks:
  traefik:
    external: true
```

**Start proxy:**

```bash
docker-compose up -d
```

### Option 2: Standalone Nginx + Let's Encrypt

If you don't have Traefik:

```bash
# Install nginx and certbot
apt-get install -y nginx certbot python3-certbot-nginx

# Create nginx config
nano /etc/nginx/sites-available/htmltopdf
```

**Nginx configuration:**

```nginx
server {
    listen 80;
    server_name htmltopdf.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/htmltopdf /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d htmltopdf.your-domain.com
```

---

## Verify Deployment

### Test Endpoints

```bash
# Health check
curl https://htmltopdf.your-domain.com/health

# Version
curl https://htmltopdf.your-domain.com/version

# PDF generation
curl -X POST https://htmltopdf.your-domain.com/convert \
  -H "X-API-Key: your-generated-key" \
  -H "Content-Type: application/json" \
  -d '{"html":"<h1>Test</h1>","filename":"test.pdf"}' \
  --output test.pdf
```

### Check Service Status

```bash
# Service status
systemctl status html-to-pdf

# View logs
journalctl -u html-to-pdf -n 50

# Access logs
tail -f /var/log/html-to-pdf-access.log

# Error logs
tail -f /var/log/html-to-pdf-error.log
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
journalctl -u html-to-pdf -n 100
```

**Common issues:**
- Missing dependencies: `pip install -r requirements.txt`
- Chromium not installed: `playwright install chromium`
- Port conflict: Check if port 5000 is available
- Permission issues: Ensure correct file ownership

### PDF Generation Fails

**Test Playwright:**
```bash
cd /opt/html-to-pdf
source venv/bin/activate
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

**Check Chromium:**
```bash
playwright install chromium
```

**Missing system libraries:**
```bash
apt-get install -y libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
  libasound2t64 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
  libxfixes3 fonts-liberation fonts-noto-color-emoji
```

### SSL/HTTPS Issues

**Traefik not routing:**
- Check docker network: `docker network ls`
- Verify labels in docker-compose.yml
- Check Traefik logs: `docker logs traefik`

**Nginx errors:**
- Test config: `nginx -t`
- Check logs: `tail -f /var/log/nginx/error.log`
- Verify domain DNS is correct

### API Key Issues

**Check API keys file:**
```bash
cat /opt/html-to-pdf/.api-keys.json
```

**Regenerate keys:**
```bash
cd /opt/html-to-pdf
source venv/bin/activate
python generate_api_key.py add "New Key"
```

### Performance Issues

**Increase workers:**

Edit `/etc/systemd/system/html-to-pdf.service`:
```ini
ExecStart=/opt/html-to-pdf/venv/bin/gunicorn \
    --workers 8 \  # Increase from 4
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    app:app
```

**Restart service:**
```bash
systemctl daemon-reload
systemctl restart html-to-pdf
```

---

## Next Steps

✅ **Deployment complete!**

**See also:**
- [API.md](API.md) - Complete API documentation
- [UPDATING.md](UPDATING.md) - Update your VPS with new code
- [README.md](README.md) - Project overview

---

## Architecture Reference

```
┌─────────────┐
│   Internet  │
└──────┬──────┘
       │ HTTPS (443)
       ▼
┌─────────────────┐
│    Traefik      │  or  Nginx
│  (SSL/Routing)  │
└──────┬──────────┘
       │ HTTP (80 or 5000)
       ▼
┌─────────────────┐
│ Nginx Container │ (Optional - if using Traefik)
│    (Proxy)      │
└──────┬──────────┘
       │ HTTP (5000)
       ▼
┌─────────────────┐
│ Systemd Service │
│   Gunicorn      │ (4 workers)
│   Port 5000     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Flask App     │
│   - Auth        │
│   - Rate Limit  │
│   - PDF Gen     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Playwright    │
│   Chromium      │
└─────────────────┘
```

---

**Deployment time:** ~15-20 minutes  
**Update time:** ~10 seconds (see [UPDATING.md](UPDATING.md))
