# Updating Your VPS

Simple guide to update your HTML-to-PDF API with new code.

---

## 🚀 Quick Update (Recommended)

### One-Command Update

**From your Windows machine:**

```powershell
.\update-vps-simple.ps1 -Auto
```

That's it! Updates in ~10 seconds with:
- ✅ Automatic API key backup
- ✅ File upload (app.py, version.json)
- ✅ Service restart
- ✅ Deployment verification
- ✅ Version confirmation

---

## 📋 First Time Setup

### Enable Passwordless SSH (One-Time)

**1. Generate SSH key:**

```powershell
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa" -N '""' -C "vps-access"
```

**2. Copy key to VPS:**

```powershell
$pubkey = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"
ssh root@htmltopdf.your-domain.com "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$pubkey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

**3. Test connection** (should not ask for password):

```powershell
ssh root@htmltopdf.your-domain.com "echo 'SSH key works!'"
```

✅ **Done!** Now updates require zero interaction.

---

## 📦 Update Options

### Standard Update

```powershell
.\update-vps-simple.ps1 -Auto
```

Uploads:
- `app.py` - Main application
- `version.json` - Version info

### Update with Dependencies

If you changed `requirements.txt`:

```powershell
.\update-vps-simple.ps1 -Auto -UpdateDeps
```

Also uploads and installs:
- `requirements.txt`
- Updates Python packages

### Interactive Update

Want confirmation before updating:

```powershell
.\update-vps-simple.ps1
```

Will ask: "Update VPS with local changes? (y/n)"

### Skip API Key Backup

If you're testing frequently:

```powershell
.\update-vps-simple.ps1 -Auto -SkipBackup
```

---

## 🔧 Manual Update (Alternative)

If you prefer manual control:

### Step 1: Backup API Keys

```powershell
ssh root@your-domain.com "cp /opt/html-to-pdf/.api-keys.json /root/.api-keys-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
```

### Step 2: Upload Files

```powershell
scp app.py version.json root@your-domain.com:/opt/html-to-pdf/
```

### Step 3: Restart Service

```powershell
ssh root@your-domain.com "systemctl restart html-to-pdf"
```

### Step 4: Verify

```powershell
# Check status
ssh root@your-domain.com "systemctl status html-to-pdf --no-pager | head -15"

# Check version
curl https://your-domain.com/version

# Test health
curl https://your-domain.com/health
```

---

## 🎯 What the Update Script Does

```
========================================
  HTML-to-PDF VPS Update Script
========================================

Backing up API keys...
✓ API keys backed up

Uploading updated files...
app.py                    100%   26KB
version.json              100%  765B
✓ Files uploaded successfully

Restarting service...
✓ Service restarted

Service status...
● html-to-pdf.service - Active (running)
  Memory: 89.3M
  Tasks: 5 (1 master + 4 workers)

Verifying update...
Version: 2.1.0
Updated: 2026-01-06

Recent changes:
  • Enhanced filename parameter
  • Security sanitization
  • Dynamic filename support

========================================
  ✓ Update completed successfully!
========================================
```

---

## 📊 Update Workflow

```
┌──────────────────┐
│  Local Changes   │
│  - Edit app.py   │
│  - Update version│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Run Script     │
│ update-vps-      │
│ simple.ps1 -Auto │
└────────┬─────────┘
         │
         ├─► Backup API keys
         ├─► Upload files (SCP)
         ├─► Restart service
         └─► Verify deployment
                 │
                 ▼
         ┌──────────────────┐
         │   VPS Updated    │
         │   Version: 2.1.0 │
         │   Status: ✓ OK   │
         └──────────────────┘
```

---

## 🛠️ Troubleshooting

### SSH Key Not Working

**Test connection:**
```powershell
ssh -v root@your-domain.com
```

**Regenerate and re-add:**
```powershell
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa_new" -N '""'
$pubkey = Get-Content "$env:USERPROFILE\.ssh\id_rsa_new.pub"
ssh root@your-domain.com "echo '$pubkey' >> ~/.ssh/authorized_keys"
```

### Upload Fails

**Check connectivity:**
```powershell
Test-NetConnection your-domain.com -Port 22
```

**Manually test SCP:**
```powershell
scp version.json root@your-domain.com:/tmp/test.json
```

### Service Won't Restart

**Check logs:**
```powershell
ssh root@your-domain.com "journalctl -u html-to-pdf -n 50"
```

**Test Python syntax:**
```powershell
ssh root@your-domain.com "cd /opt/html-to-pdf && python3 -m py_compile app.py"
```

### Version Doesn't Change

**Check uploaded files:**
```powershell
ssh root@your-domain.com "ls -lh /opt/html-to-pdf/app.py /opt/html-to-pdf/version.json"
```

**View version file:**
```powershell
ssh root@your-domain.com "cat /opt/html-to-pdf/version.json"
```

**Force restart:**
```powershell
ssh root@your-domain.com "systemctl stop html-to-pdf && sleep 2 && systemctl start html-to-pdf"
```

### API Keys Lost

**Restore from backup:**
```powershell
# List backups
ssh root@your-domain.com "ls -lh /root/.api-keys-backup*"

# Restore latest
ssh root@your-domain.com "cp /root/.api-keys-backup-YYYYMMDD-HHMMSS.json /opt/html-to-pdf/.api-keys.json"

# Restart service
ssh root@your-domain.com "systemctl restart html-to-pdf"
```

---

## 📝 Files Updated

The update script handles these files:

| File | Description | Always Updated? |
|------|-------------|-----------------|
| `app.py` | Main application | ✅ Yes |
| `version.json` | Version info | ✅ Yes |
| `requirements.txt` | Dependencies | ⚠️ Only with `-UpdateDeps` |
| `.api-keys.json` | API keys | ❌ Never (backed up only) |

**Never uploaded** (kept on VPS):
- `.api-keys.json` - Server-specific configuration
- `venv/` - Virtual environment
- `__pycache__/` - Auto-generated cache

---

## 🔄 Advanced: Git-Based Updates

### Setup Git on VPS (One-Time)

```bash
# SSH into VPS
ssh root@your-domain.com

# Navigate to app directory
cd /opt/html-to-pdf

# Initialize git (if not already)
git init
git remote add origin https://github.com/yourusername/HTML-to-PDF.git

# Or clone fresh
cd /opt
rm -rf html-to-pdf
git clone https://github.com/yourusername/HTML-to-PDF.git html-to-pdf
cd html-to-pdf

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Update from GitHub

```bash
ssh root@your-domain.com << 'EOF'
cd /opt/html-to-pdf
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart html-to-pdf
systemctl status html-to-pdf
EOF
```

---

## ⚡ Quick Reference

| Task | Command |
|------|---------|
| **Standard update** | `.\update-vps-simple.ps1 -Auto` |
| **With dependencies** | `.\update-vps-simple.ps1 -Auto -UpdateDeps` |
| **Interactive** | `.\update-vps-simple.ps1` |
| **Skip backup** | `.\update-vps-simple.ps1 -Auto -SkipBackup` |
| **Check service** | `ssh root@your-domain.com "systemctl status html-to-pdf"` |
| **View logs** | `ssh root@your-domain.com "journalctl -u html-to-pdf -n 50"` |
| **Test API** | `curl https://your-domain.com/health` |
| **Check version** | `curl https://your-domain.com/version` |

---

## 📚 Related Documentation

- [README.md](README.md) - Project overview
- [API.md](API.md) - Complete API documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Initial deployment guide

---

**Update time:** ~10 seconds  
**Downtime:** <1 second (service restart)  
**Frequency:** As often as needed (automated)
