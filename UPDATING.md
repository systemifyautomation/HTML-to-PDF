# Updating Production from GitHub

This guide covers how to update your production deployment when you push changes to GitHub.

## Overview

The recommended workflow:

1. **Develop locally** → Test changes
2. **Commit & push** to GitHub
3. **Pull & deploy** on production VPS
4. **Verify** the update worked

## Initial Setup (One-Time)

If you originally deployed by uploading files manually, convert to git-based deployment:

```bash
# SSH into VPS
ssh root@your-vps.example.com

# Backup current installation
cp -r /opt/html-to-pdf /opt/html-to-pdf.backup

# Remove old directory
rm -rf /opt/html-to-pdf

# Clone from GitHub
cd /opt
git clone https://github.com/YOUR_USERNAME/HTML-to-PDF.git html-to-pdf

# Restore API keys (DO NOT commit these!)
cp /opt/html-to-pdf.backup/.api-keys.json /opt/html-to-pdf/
chmod 600 /opt/html-to-pdf/.api-keys.json

# Install dependencies
cd /opt/html-to-pdf
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Restart service
systemctl restart html-to-pdf
```

## Update Process

### Automatic Update (Recommended)

Use the included update script for safe, automated updates:

```bash
# SSH into VPS
ssh root@your-vps.example.com

# Run update script
sudo /opt/html-to-pdf/deployment/update-from-github.sh
```

**What it does**:
1. ✅ Stops the service safely
2. ✅ Backs up current state
3. ✅ Pulls latest changes from GitHub
4. ✅ Updates dependencies if needed
5. ✅ Reinstalls Playwright browser if version changed
6. ✅ Restarts the service
7. ✅ Runs health checks
8. ✅ Shows what changed

### Manual Update

If you prefer manual control:

```bash
# SSH into VPS
ssh root@your-vps.example.com

# Navigate to app directory
cd /opt/html-to-pdf

# Stop service
sudo systemctl stop html-to-pdf

# Pull latest changes
git pull origin main

# If requirements.txt changed, update dependencies
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Restart service
sudo systemctl start html-to-pdf

# Check status
sudo systemctl status html-to-pdf

# Test health endpoint
curl http://localhost:5000/health
curl https://htmltopdf.example.com/health
```

## Development Workflow

### 1. Local Development

```bash
# Make your changes locally
cd C:\Users\YourUser\Documents\GitHub\HTML-to-PDF

# Test locally
python app.py
```

### 2. Commit and Push

```bash
# Stage changes
git add app.py

# Commit with descriptive message
git commit -m "Add new feature: PDF margins customization"

# Push to GitHub
git push origin main
```

### 3. Deploy to Production

```bash
# SSH into production
ssh root@your-vps.example.com

# Run update script
sudo /opt/html-to-pdf/deployment/update-from-github.sh
```

### 4. Verify Deployment

```bash
# Check service is running
systemctl status html-to-pdf

# Test endpoints
curl https://htmltopdf.example.com/health
curl https://htmltopdf.example.com/version

# Generate test PDF
curl -X POST https://htmltopdf.example.com/convert \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"html":"<h1>Test</h1>"}' \
  -o test.pdf
```

## Version Tagging (Best Practice)

Use git tags to track production versions:

```bash
# After successful deployment, tag the release
git tag -a v2.1.0 -m "Release 2.1.0: Added PDF margins"
git push origin v2.1.0

# On VPS, you can checkout specific versions
cd /opt/html-to-pdf
git checkout v2.1.0
systemctl restart html-to-pdf
```

## Rollback to Previous Version

If an update causes issues:

### Quick Rollback

```bash
# SSH into VPS
ssh root@your-vps.example.com
cd /opt/html-to-pdf

# View commit history
git log --oneline -10

# Rollback to previous commit
git reset --hard HEAD~1

# Restart service
systemctl restart html-to-pdf
```

### Rollback to Specific Version

```bash
# Using commit hash
git checkout abc1234

# Or using tag
git checkout v2.0.0

# Restart service
systemctl restart html-to-pdf
```

## Troubleshooting Updates

### Update Script Fails

```bash
# Check service logs
journalctl -u html-to-pdf -n 50

# Check git status
cd /opt/html-to-pdf
git status

# If there are conflicts, stash local changes
git stash
git pull origin main

# Restart service manually
systemctl restart html-to-pdf
```

### Dependencies Won't Install

```bash
# Update pip first
source venv/bin/activate
pip install --upgrade pip

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall

# Reinstall Playwright
playwright install chromium
playwright install-deps chromium
```

### Service Won't Start After Update

```bash
# Check detailed logs
journalctl -u html-to-pdf -n 100 --no-pager

# Check for syntax errors
cd /opt/html-to-pdf
source venv/bin/activate
python3 -c "import app"

# Rollback if needed
git checkout HEAD~1
systemctl restart html-to-pdf
```

## Monitoring After Updates

```bash
# Real-time logs
journalctl -u html-to-pdf -f

# Access logs
tail -f /var/log/html-to-pdf-access.log

# Error logs
tail -f /var/log/html-to-pdf-error.log

# System resource usage
htop
```

## Best Practices

1. **Always test locally** before pushing to GitHub
2. **Use meaningful commit messages** so you know what changed
3. **Tag releases** for easy version tracking and rollback
4. **Monitor logs** for 5-10 minutes after updates
5. **Keep API keys backed up** securely (not in git!)
6. **Test the health endpoint** after every update
7. **Update during low-traffic periods** if possible
8. **Have a rollback plan** ready

## Scheduled Updates

For automated updates, create a cron job (use with caution):

```bash
# Edit crontab
crontab -e

# Add line to update every night at 2 AM
0 2 * * * /opt/html-to-pdf/deployment/update-from-github.sh >> /var/log/html-to-pdf-auto-update.log 2>&1
```

**Warning**: Automatic updates can break production if not tested. Only use for minor updates.

## CI/CD Integration (Advanced)

For automated testing and deployment, consider GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
    
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            /opt/html-to-pdf/deployment/update-from-github.sh
```

---

**Remember**: The update script is included in `deployment/update-from-github.sh` and handles everything automatically!
