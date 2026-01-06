# Production Deployment Guide

## Overview

This guide documents the deployment of the HTML-to-PDF converter to a VPS with **coexisting Traefik/n8n infrastructure**.

## Architecture

The deployment uses a **hybrid architecture** to enable HTTPS access while preserving existing services:

```
Internet (HTTPS)
    ↓
Traefik (Docker) - Port 80/443
    ↓
Nginx Proxy Container (Docker)
    ↓
HTML-to-PDF Service (Systemd)
    ↓
Gunicorn + Flask + Playwright
```

### Why This Architecture?

**Problem**: Traefik already owns ports 80/443 for n8n, so we can't bind nginx directly to those ports.

**Solution**: 
1. Run the main application as a **systemd service** (reliable, auto-restart)
2. Create a lightweight **nginx container** that proxies to the systemd service
3. Let **Traefik route** HTTPS traffic to the nginx container
4. Everything works together without port conflicts

## Deployment Steps

### 1. Prepare the VPS

```bash
# SSH into your VPS
ssh root@your-vps.example.com

# Install git if not already installed
apt-get update && apt-get install -y git
```

### 2. Clone Repository from GitHub

**Recommended Method** - Deploy directly from version control:

```bash
# Clone the repository
cd /opt
git clone https://github.com/YOUR_USERNAME/HTML-to-PDF.git html-to-pdf

# Navigate to directory
cd html-to-pdf
```

**Alternative: Manual Upload** (not recommended):

```powershell
# Create directory on VPS
ssh root@your-vps.example.com "mkdir -p /opt/html-to-pdf"

# Upload files from local machine
scp -r app.py requirements.txt generate_api_key.py root@your-vps.example.com:/opt/html-to-pdf/
scp -r deployment root@your-vps.example.com:/opt/html-to-pdf/
```

**Important**: Never commit `.api-keys.json` to GitHub! You'll create this file on the server.

### 3. Install Python Dependencies

On the VPS:

```bash
cd /opt/html-to-pdf

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Install Chromium system dependencies
apt-get update
apt-get install -y libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
  libasound2t64 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
  libxfixes3 fonts-liberation fonts-noto-color-emoji
```

### 4. Configure API Keys

```bash
cd /opt/html-to-pdf

# Activate virtual environment
source venv/bin/activate

# Generate your API keys
python3 generate_api_key.py

# Edit the generated .api-keys.json file
nano .api-keys.json

# Set secure permissions
chmod 600 .api-keys.json
```

**Important**: 
- Never commit `.api-keys.json` to version control
- The `.gitignore` file already excludes this
- Keep a secure backup: `cp .api-keys.json /secure/backup/`

### 5. Create Systemd Service

Create `/etc/systemd/system/html-to-pdf.service`:

```ini
[Unit]
Description=HTML-to-PDF Converter API
After=network.target

[Service]
Type=simple
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

**Key Configuration**:
- `--bind 0.0.0.0:5000` - Listens on all interfaces so Docker can reach it
- `--workers 4` - 4 worker processes for concurrent PDF generation
- `--timeout 120` - 2 minutes for complex PDF rendering
- `Restart=always` - Auto-restart on crashes

Enable and start the service:

The `traefik-proxy` directory is already included in the repository.

Navigate to it and deploy:

```bash
cd /opt/html-to-pdf/deployment/traefik-proxy
```

**Important**: Edit `docker-compose.yml` first to update:
- Your domain name
- Traefik network name  
- Cert resolver name

**Dockerfile** (already included)le html-to-pdf
systemctl start html-to-pdf
systemctl status html-to-pdf
```

### 6. Create Traefik Proxy Container

Create directory: `/opt/html-to-pdf/traefik-proxy/`

**Dockerfile**:
```dockerfile
FROM nginx:alpine

# Simple nginx config that proxies to the host systemd service
RUN echo 'server { \
    listen 80; \
    location / { \
        proxy_pass http://host.docker.internal:5000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        client_max_body_size 16M; \
        proxy_connect_timeout 120s; \
        proxy_send_timeout 120s; \
        proxy_read_timeout 120s; \
    } \
}' > /etc/nginx/conf.d/default.conf
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  htmltopdf-proxy:
    build: .
    container_name: htmltopdf-proxy
    restart: unless-stopped
    networks:
      - n8n_default  # Use your existing Traefik network
    extra_hosts:
      - "host.docker.internal:host-gateway"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.htmltopdf.rule=Host(`htmltopdf.example.com`)"
      - "traefik.http.routers.htmltopdf.entrypoints=websecure"
      - "traefik.http.routers.htmltopdf.tls.certresolver=mytlschallenge"
      - "traefik.http.services.htmltopdf.loadbalancer.server.port=80"

networks:
  n8n_default:
    external: true
```

**Important**: Replace:
- `htmltopdf.example.com` with your actual domain
- `mytlschallenge` with your Traefik cert resolver name
- `n8n_default` with your actual Docker network name

Deploy the container:

```bash
cd /opt/html-to-pdf/traefik-proxy
docker-compose up -d --build
```

### 7. Optional: Configure Nginx (HTTP on Port 9000)

For direct HTTP access (bypassing Traefik):

Create `/etc/nginx/sites-available/htmltopdf.conf`:

```nginx
server {
    listen 9000;
    server_name htmltopdf.example.com;

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

Enable and restart nginx:

```bash
ln -s /etc/nginx/sites-available/htmltopdf.conf /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## DNS Configuration

Add an A record pointing to your VPS:

```
Type: A
Host: htmltopdf
Value: YOUR_VPS_IP
TTL: 3600
```

## Verification

### 1. Check Systemd Service

```bash
systemctl status html-to-pdf
journalctl -u html-to-pdf -n 50
```

### 2. Check Docker Container

```bash
docker ps | grep htmltopdf
docker logs htmltopdf-proxy
```

### 3. Test Health Endpoint

```bash
# Via HTTPS (Traefik)
curl https://htmltopdf.example.com/health

# Via HTTP (nginx)
curl http://htmltopdf.example.com:9000/health

# Expected response:
# {"status":"healthy","timestamp":"...","version":"2.0.0"}
```

### 4. Test PDF Generation

```bash
curl -X POST https://htmltopdf.example.com/convert \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"html":"<h1>Test</h1>"}' \
  -o test.pdf
```

## Monitoring

### View Application Logs

```bash
# Real-time logs
journalctl -u html-to-pdf -f

# Access logs
tail -f /var/log/html-to-pdf-access.log

# Error logs
tail -f /var/log/html-to-pdf-error.log
```

### Check Resource Usage

```bash
# Service status
systemctl status html-to-pdf

# Process details
ps aux | grep gunicorn

# Memory usage
free -h
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
systemctl status html-to-pdf

# View detailed logs
journalctl -u html-to-pdf -n 100 --no-pager

# Common issues:
# 1. Port 5000 already in use: lsof -i :5000
# 2. Missing dependencies: source venv/bin/activate && pip install -r requirements.txt
# 3. Missing Chromium: playwright install chromium
```

### 404 Errors from Traefik

```bash
# Check if container is on the correct network
docker inspect htmltopdf-proxy | grep -A 5 Networks

# Check Traefik logs
docker logs traefik-container-name

# Verify labels
docker inspect htmltopdf-proxy | grep -A 20 Labels
```

### Chromium Browser Errors

```bash
# Install missing system libraries
apt-get install -y libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
  libasound2t64 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
  libxfixes3 fonts-liberation fonts-noto-color-emoji

# Restart service
systemctl restart html-to-pdf
```

### PDF Generation Fails

```bash
# Check error logs
tail -n 50 /var/log/html-to-pdf-error.log

# Test Chromium directly
cd /opt/html-to-pdf
source venv/bin/activate
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); print('OK'); browser.close(); p.stop()"
```

## Updates and Maintenance

### Method 1: Update from GitHub (Recommended)

This is the recommended method for production updates. It ensures you're always deploying from version control.

#### Initial Setup: Clone Repository on VPS

```bash
# First time only: Clone the repository
cd /opt
git clone https://github.com/YOUR_USERNAME/HTML-to-PDF.git html-to-pdf-repo

# Create symlink to application directory
ln -s /opt/html-to-pdf-repo /opt/html-to-pdf

# Install dependencies
cd /opt/html-to-pdf
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Copy API keys from secure location (DO NOT commit to git!)
cp /secure/backup/.api-keys.json /opt/html-to-pdf/.api-keys.json
chmod 600 /opt/html-to-pdf/.api-keys.json
```

#### Update Process: Pull Latest Changes

```bash
# Stop the service
systemctl stop html-to-pdf

# Navigate to repository
cd /opt/html-to-pdf-repo

# Backup current state (optional but recommended)
git branch backup-$(date +%Y%m%d-%H%M%S)

# Pull latest changes from GitHub
git pull origin main

# Update dependencies if requirements.txt changed
source venv/bin/activate
pip install -r requirements.txt

# Update Playwright if needed
playwright install chromium

# Restart service
systemctl start html-to-pdf

# Check status
systemctl status html-to-pdf

# Verify it's working
curl http://localhost:5000/health
```

#### Automated Update Script

Create `/opt/html-to-pdf/update.sh` for easy updates:

```bash
#!/bin/bash
set -e

echo "🔄 Updating HTML-to-PDF service from GitHub..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop service
echo -e "${YELLOW}Stopping service...${NC}"
systemctl stop html-to-pdf

# Backup current commit
cd /opt/html-to-pdf
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo -e "${YELLOW}Current commit: $CURRENT_COMMIT${NC}"

# Pull latest changes
echo -e "${YELLOW}Pulling from GitHub...${NC}"
git pull origin main

# Check if requirements changed
if git diff --name-only $CURRENT_COMMIT HEAD | grep -q "requirements.txt"; then
    echo -e "${YELLOW}requirements.txt changed, updating dependencies...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium
fi

# Start service
echo -e "${YELLOW}Starting service...${NC}"
systemctl start html-to-pdf

# Wait for service to start
sleep 3

# Check health
echo -e "${YELLOW}Checking health...${NC}"
if curl -s http://localhost:5000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Update successful! Service is healthy.${NC}"
    NEW_COMMIT=$(git rev-parse --short HEAD)
    echo -e "${GREEN}Updated from $CURRENT_COMMIT to $NEW_COMMIT${NC}"
else
    echo -e "${YELLOW}⚠️  Service started but health check failed${NC}"
    systemctl status html-to-pdf
fi

# Show recent commits
echo -e "\n${YELLOW}Recent changes:${NC}"
git log --oneline -5
```

Make it executable:

```bash
chmod +x /opt/html-to-pdf/update.sh
```

Then update with a single command:

```bash
/opt/html-to-pdf/update.sh
```

#### Rollback to Previous Version

If an update causes issues:

```bash
cd /opt/html-to-pdf

# View recent commits
git log --oneline -10

# Rollback to specific commit
git checkout COMMIT_HASH

# Restart service
systemctl restart html-to-pdf

# Or use git revert for safer rollback
git revert HEAD
systemctl restart html-to-pdf
```

### Method 2: Manual File Upload (Not Recommended)

Only use this for quick hotfixes. For regular updates, use Method 1.

```bash
cd /opt/html-to-pdf

# Backup current version
cp app.py app.py.backup

# Upload new files from local machine
scp app.py root@your-vps.example.com:/opt/html-to-pdf/

# Restart service
systemctl restart html-to-pdf
```

### Update Dependencies Only

```bash
cd /opt/html-to-pdf
source venv/bin/activate
pip install --upgrade playwright
playwright install chromium
systemctl restart html-to-pdf
```

### Update Proxy Container

```bash
cd /opt/html-to-pdf/traefik-proxy
docker-compose down
docker-compose up -d --build
```

### Best Practices for Updates

1. **Always test locally first** before pushing to GitHub
2. **Use git tags** for version tracking:
   ```bash
   git tag v2.0.1
   git push origin v2.0.1
   ```
3. **Monitor logs** during updates:
   ```bash
   journalctl -u html-to-pdf -f
   ```
4. **Keep backups** of `.api-keys.json`:
   ```bash
   cp /opt/html-to-pdf/.api-keys.json /secure/backup/api-keys-$(date +%Y%m%d).json
   ```
5. **Test the health endpoint** after every update:
   ```bash
   curl http://localhost:5000/health
   curl https://htmltopdf.example.com/health
   ```

## Security Considerations

1. **API Keys**: Store in `/opt/html-to-pdf/.api-keys.json` with restricted permissions:
   ```bash
   chmod 600 /opt/html-to-pdf/.api-keys.json
   ```

2. **Firewall**: Only expose necessary ports (80, 443 via Traefik)
   ```bash
   # Block direct access to port 5000
   ufw deny 5000
   ```

3. **Log Rotation**: Configure logrotate for application logs:
   ```bash
   # /etc/logrotate.d/html-to-pdf
   /var/log/html-to-pdf-*.log {
       daily
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 root root
       sharedscripts
       postrotate
           systemctl reload html-to-pdf
       endscript
   }
   ```

4. **Updates**: Regularly update system packages and Python dependencies

## Performance Tuning

### Gunicorn Workers

Adjust worker count based on CPU cores:

```ini
# In /etc/systemd/system/html-to-pdf.service
--workers 4  # Rule of thumb: (2 × CPU_cores) + 1
```

### Timeout Settings

For large/complex PDFs, increase timeout:

```ini
--timeout 180  # 3 minutes for very large documents
```

### Memory Limits

Set memory limits to prevent runaway processes:

```ini
[Service]
MemoryMax=2G
MemoryHigh=1.5G
```

## Backup Strategy

### Files to Backup

1. `/opt/html-to-pdf/.api-keys.json` - API keys (encrypted)
2. `/opt/html-to-pdf/app.py` - Application code
3. `/etc/systemd/system/html-to-pdf.service` - Service configuration
4. `/var/log/html-to-pdf-*.log` - Logs (optional)

### Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/backup/html-to-pdf-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR
cp /opt/html-to-pdf/.api-keys.json $BACKUP_DIR/
cp /opt/html-to-pdf/app.py $BACKUP_DIR/
cp /etc/systemd/system/html-to-pdf.service $BACKUP_DIR/
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
```

## Support

For issues or questions:
- Check logs: `journalctl -u html-to-pdf -n 100`
- Review this documentation
- Check GitHub issues (if public repo)

---

**Last Updated**: January 6, 2026
**Version**: 2.0.0
