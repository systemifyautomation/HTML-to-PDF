# 🔄 Redeployment Guide - Update Your VPS with Latest Changes

**Quick guide to pull changes from GitHub and redeploy on your Hostinger VPS**

---

## 📋 Quick Reference

### With Docker (Recommended)
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF
git pull origin main
cd ~
docker compose restart htmltopdf
```

### With Systemd (Traditional)
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF
git pull origin main
systemctl restart htmltopdf
```

### Full Redeploy (Dependencies Changed)
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart htmltopdf
```

---

## 🚀 Step-by-Step Redeployment

### Method 1: Basic Update (Code Changes Only)

**Use this when you've only changed Python code (app.py, etc.)**

#### Step 1: Connect to VPS
```bash
ssh root@YOUR_VPS_IP
```

#### Step 2: Navigate to Project
```bash
cd ~/HTML-to-PDF
```

#### Step 3: Check Current Status
```bash
# See what branch you're on
git status

# See recent commits
git log --oneline -5
```

#### Step 4: Pull Latest Changes
```bash
git pull origin main
```

**Expected output:**
```
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 3 (delta 2), reused 0 (delta 0)
Unpacking objects: 100% (3/3), done.
From https://github.com/systemifyautomation/HTML-to-PDF
   abc1234..def5678  main -> origin/main
Updating abc1234..def5678
Fast-forward
 app.py | 10 +++++-----
 1 file changed, 5 insertions(+), 5 deletions(-)
```

#### Step 5: Restart Service
```bash
systemctl restart htmltopdf
```

#### Step 6: Verify Service is Running
```bash
systemctl status htmltopdf
```

**Look for:**
```
● htmltopdf.service - HTML to PDF Converter API
     Active: active (running)
```

#### Step 7: Test the API
```bash
# Test health endpoint
curl https://yourdomain.com/health

# Or from your local machine
curl https://htmltopdf.systemifyautomation.com/health
```

**✅ Done! Your changes are live.**

---

### Method 2: Full Redeploy (Dependencies or Configuration Changed)

**Use this when you've updated:**
- `requirements.txt` (new Python packages)
- System dependencies
- Configuration files
- `.api-keys.json` structure

#### Step 1: Connect to VPS
```bash
ssh root@YOUR_VPS_IP
```

#### Step 2: Stop the Service
```bash
systemctl stop htmltopdf
```

#### Step 3: Navigate and Pull Changes
```bash
cd ~/HTML-to-PDF
git pull origin main
```

#### Step 4: Activate Virtual Environment
```bash
source venv/bin/activate
```

**Your prompt should show `(venv)` prefix:**
```
(venv) root@server:~/HTML-to-PDF#
```

#### Step 5: Update Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 6: Update System Dependencies (if needed)
```bash
# Only if you added new system libraries
apt-get update
apt-get install -y NEW_PACKAGE_NAME
```

#### Step 7: Update Configuration Files (if changed)

**If systemd service file changed:**
```bash
cp deployment/htmltopdf.service /etc/systemd/system/
systemctl daemon-reload
```

**If nginx config changed:**
```bash
cp deployment/nginx.conf /etc/nginx/sites-available/htmltopdf
nginx -t  # Test configuration
systemctl reload nginx
```

**If API keys structure changed:**
```bash
# Backup current keys
cp .api-keys.json .api-keys.json.backup

# Update with new structure (manually edit)
nano .api-keys.json
```

#### Step 8: Restart Service
```bash
systemctl start htmltopdf
systemctl enable htmltopdf  # Ensure it starts on boot
```

#### Step 9: Verify Everything Works
```bash
# Check service status
systemctl status htmltopdf

# View live logs
journalctl -u htmltopdf -f

# Test API
curl https://yourdomain.com/health
```

---

### Method 3: Docker Redeploy (Recommended)

**Use this if you deployed with Docker Compose**

#### Step 1: Connect and Navigate
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF
```

#### Step 2: Pull Latest Code
```bash
git pull origin main
```

#### Step 3: Restart Container
```bash
cd ~
docker compose restart htmltopdf
```

**That's it!** The container will use the updated code from the mounted directory.

#### Step 4: Check Logs (Optional)
```bash
docker compose logs -f htmltopdf
```

#### Step 5: Test
```bash
curl https://yourdomain.com/health
```

---

#### Alternative: Full Rebuild (Only if dependencies changed)

If `requirements.txt` or `Dockerfile` changed:

```bash
cd ~/HTML-to-PDF
git pull origin main
cd ~
docker compose up -d --build htmltopdf
```

---

## 🔧 Common Redeployment Scenarios

### Scenario 1: Fixed a Bug in app.py
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF
git pull origin main
systemctl restart htmltopdf
systemctl status htmltopdf
```

### Scenario 2: Added New API Endpoint
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF
git pull origin main
systemctl restart htmltopdf

# Test new endpoint
curl -X POST https://yourdomain.com/new-endpoint \
  -H "X-API-Key: YOUR_KEY"
```

### Scenario 3: Updated Python Package Version
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart htmltopdf
```

### Scenario 4: Changed Gunicorn Workers or Timeout
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF
git pull origin main
cp deployment/htmltopdf.service /etc/systemd/system/
systemctl daemon-reload
systemctl restart htmltopdf
```

### Scenario 5: Updated Nginx Configuration
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF
git pull origin main
cp deployment/nginx.conf /etc/nginx/sites-available/htmltopdf
nginx -t
systemctl reload nginx
```

### Scenario 6: Added New API Keys
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF

# Generate new key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Edit keys file
nano .api-keys.json

# Add new key to the api_keys array, then save

# Restart to reload keys
systemctl restart htmltopdf
```

---

## 🛠️ Automated Deployment Scripts

### For Docker (Recommended)

Create a deployment script for one-command updates:

```bash
nano ~/HTML-to-PDF/update-docker.sh
```

**Add this content:**
```bash
#!/bin/bash

echo "🚀 Starting Docker deployment..."

# Navigate to project
cd ~/HTML-to-PDF

# Pull latest changes
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Navigate to docker compose location
cd ~

# Restart container
echo "🔄 Restarting Docker container..."
docker compose restart htmltopdf

# Wait a moment for service to start
sleep 3

# Check status
if docker compose ps htmltopdf | grep -q "Up"; then
    echo "✅ Deployment successful! Container is running."
    
    # Test API
    echo "🧪 Testing API..."
    curl -s https://htmltopdf.systemifyautomation.com/health
    echo ""
    
    # Show version
    echo "📋 Current version:"
    curl -s https://htmltopdf.systemifyautomation.com/version | grep -o '"version":"[^"]*"'
    echo ""
else
    echo "❌ Deployment failed! Container is not running."
    echo "📋 Checking logs..."
    docker compose logs --tail=20 htmltopdf
    exit 1
fi

echo "🎉 Deployment complete!"
```

**Make it executable:**
```bash
chmod +x ~/HTML-to-PDF/update-docker.sh
```

**Use it:**
```bash
ssh root@YOUR_VPS_IP
~/HTML-to-PDF/update-docker.sh
```

---

### For Systemd (Traditional)

Create a deployment script for systemd-based deployments:

```bash
nano ~/HTML-to-PDF/update.sh
```

**Add this content:**
```bash
#!/bin/bash

echo "🚀 Starting deployment..."

# Navigate to project
cd ~/HTML-to-PDF

# Pull latest changes
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Check if requirements.txt changed
if git diff HEAD@{1} --name-only | grep -q requirements.txt; then
    echo "📦 Requirements changed, updating packages..."
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Restart service
echo "🔄 Restarting service..."
systemctl restart htmltopdf

# Wait a moment for service to start
sleep 2

# Check status
if systemctl is-active --quiet htmltopdf; then
    echo "✅ Deployment successful! Service is running."
    
    # Test API
    echo "🧪 Testing API..."
    curl -s https://htmltopdf.systemifyautomation.com/health
    echo ""
else
    echo "❌ Deployment failed! Service is not running."
    echo "📋 Checking logs..."
    journalctl -u htmltopdf -n 20 --no-pager
    exit 1
fi

echo "🎉 Deployment complete!"
```

**Make it executable:**
```bash
chmod +x ~/HTML-to-PDF/update.sh
```

**Use it:**
```bash
ssh root@YOUR_VPS_IP
~/HTML-to-PDF/update.sh
```

---

## 📊 Viewing Logs After Deployment

### Docker Logs
```bash
# View last 50 lines
docker compose logs --tail=50 htmltopdf

# Follow logs in real-time
docker compose logs -f htmltopdf

# View logs with timestamps
docker compose logs -f --timestamps htmltopdf
```

### Service Logs (Systemd)
```bash
# View last 50 lines
journalctl -u htmltopdf -n 50

# Follow logs in real-time
journalctl -u htmltopdf -f

# View logs from last hour
journalctl -u htmltopdf --since "1 hour ago"
```

### Application Logs
```bash
# Access logs
tail -f /var/log/htmltopdf-access.log

# Error logs
tail -f /var/log/htmltopdf-error.log

# Last 100 lines
tail -n 100 /var/log/htmltopdf-error.log
```

### Nginx Logs
```bash
# Access logs
tail -f /var/log/nginx/access.log

# Error logs
tail -f /var/log/nginx/error.log
```

---

## ⚠️ Troubleshooting Failed Deployments

### Issue: Service Won't Start After Update

**Check logs:**
```bash
journalctl -u htmltopdf -n 50
```

**Common fixes:**
```bash
# Check for syntax errors
cd ~/HTML-to-PDF
source venv/bin/activate
python3 -c "import app"

# Verify API keys file exists
ls -la .api-keys.json

# Check file permissions
chown -R root:root ~/HTML-to-PDF
```

### Issue: Old Version Still Running

**Force restart:**
```bash
systemctl stop htmltopdf
pkill -f gunicorn
systemctl start htmltopdf
```

### Issue: Changes Not Reflected

**Check you're on the right branch:**
```bash
cd ~/HTML-to-PDF
git branch  # Should show * main
git log --oneline -1  # Should show your latest commit
```

**Hard reset to remote (WARNING: Loses local changes):**
```bash
git fetch origin
git reset --hard origin/main
systemctl restart htmltopdf
```

### Issue: Merge Conflicts

**If you edited files on VPS:**
```bash
# Stash local changes
git stash

# Pull latest
git pull origin main

# Reapply your changes
git stash pop

# Resolve conflicts manually
nano CONFLICTED_FILE

# Then restart
systemctl restart htmltopdf
```

---

## 🔄 Rollback to Previous Version

### Quick Rollback (Last Commit)
```bash
ssh root@YOUR_VPS_IP
cd ~/HTML-to-PDF

# Go back one commit
git reset --hard HEAD~1

# Restart service
systemctl restart htmltopdf
```

### Rollback to Specific Version
```bash
# View commit history
git log --oneline -10

# Rollback to specific commit
git reset --hard COMMIT_HASH

# Example:
git reset --hard abc1234

# Restart
systemctl restart htmltopdf
```

### Return to Latest After Rollback
```bash
git pull origin main
systemctl restart htmltopdf
```

---

## 📝 Deployment Checklist

Before deploying:
- [ ] Test changes locally (if possible)
- [ ] Commit and push to GitHub
- [ ] Note the commit hash or tag
- [ ] Backup `.api-keys.json` if structure changed

During deployment:
- [ ] SSH into VPS
- [ ] Navigate to project directory
- [ ] Pull latest changes
- [ ] Update dependencies if needed
- [ ] Restart service
- [ ] Check service status

After deployment:
- [ ] Test health endpoint
- [ ] Test main API functionality
- [ ] Check logs for errors
- [ ] Monitor for a few minutes
- [ ] Update documentation if needed

---

## 🎯 Best Practices

1. **Always test locally first** (when possible)
2. **Commit with clear messages** describing changes
3. **Use git tags for releases** (v1.0.0, v1.1.0, etc.)
4. **Deploy during low-traffic times** when possible
5. **Keep backup of .api-keys.json** before major updates
6. **Monitor logs** for 5-10 minutes after deployment
7. **Test critical endpoints** after each deployment
8. **Document breaking changes** in commit messages
9. **Use the automated script** for consistency
10. **Keep a rollback plan** ready

---

## 🔐 Security Notes

- **Never commit `.api-keys.json`** to Git
- **Backup keys securely** before redeploying
- **Rotate API keys periodically**
- **Update system packages** regularly:
  ```bash
  apt-get update && apt-get upgrade -y
  ```
- **Check SSL certificate expiry:**
  ```bash
  certbot certificates
  ```

---

## 📞 Quick Help

**Service not starting?**
```bash
journalctl -u htmltopdf -n 50
```

**Check what's running on port 9001:**
```bash
netstat -tulpn | grep 9001
```

**Restart everything:**
```bash
systemctl restart htmltopdf
systemctl restart nginx
```

**View all services:**
```bash
systemctl status htmltopdf
systemctl status nginx
```

---

<div align="center">

**Happy Deploying! 🚀**

*For issues, check logs first, then refer to the [troubleshooting guide](HOSTINGER_VPS_GUIDE.md#troubleshooting)*

</div>
