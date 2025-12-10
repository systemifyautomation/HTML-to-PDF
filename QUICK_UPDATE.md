# Quick VPS Update - Step by Step

## 🚀 Choose Your Method

### Method 1: One-Command Update (Easiest)

**From your Windows PowerShell:**

```powershell
# Edit these values first:
$VPSUser = "your-username"        # Your VPS username
$VPSHost = "htmltopdf.systemifyautomation.com"  # Your domain
$VPSPath = "~/HTML-to-PDF"        # App directory on VPS

# Run the update script
.\update-vps.ps1 -VPSUser $VPSUser -VPSHost $VPSHost -VPSPath $VPSPath
```

That's it! The script will:
- Upload all changed files
- Rebuild Docker container
- Restart the service
- Test the API
- Show you the results

---

### Method 2: Git Pull (If using Git)

**SSH into your VPS and run:**

```bash
cd ~/HTML-to-PDF
./update-vps.sh
```

Or manually:

```bash
cd ~/HTML-to-PDF
git pull origin main
docker-compose down
docker-compose up -d --build
docker-compose logs -f
```

---

### Method 3: Manual File Upload (No Git)

**Step 1: Upload files from Windows PowerShell**

```powershell
cd C:\Users\PCZZ3\Documents\GitHub\HTML-to-PDF

# Replace with your VPS details
scp app.py your-user@htmltopdf.systemifyautomation.com:~/HTML-to-PDF/
scp requirements.txt your-user@htmltopdf.systemifyautomation.com:~/HTML-to-PDF/
```

**Step 2: SSH and restart**

```bash
ssh your-user@htmltopdf.systemifyautomation.com

cd ~/HTML-to-PDF
docker-compose down
docker-compose up -d --build
```

---

## ✅ Verify Update

**Test the API:**

```bash
curl https://htmltopdf.systemifyautomation.com/
```

Look for this in the response:
```json
{
  "usage": {
    "improvements": [
      "Automatic HTML structure validation and correction",
      "Smart page break handling",
      ...
    ]
  }
}
```

**Test new features:**

```bash
curl -X POST https://htmltopdf.systemifyautomation.com/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR-KEY" \
  -d '{
    "html": "<h1>Test</h1>",
    "page_size": "Letter",
    "margin": "1in"
  }' \
  --output test.pdf
```

---

## 🐛 Troubleshooting

### Container won't start?

```bash
# Check logs
docker-compose logs

# Rebuild without cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Files not uploading?

```powershell
# Test SSH connection
ssh your-user@htmltopdf.systemifyautomation.com "echo 'Connection OK'"

# Check file exists locally
Test-Path C:\Users\PCZZ3\Documents\GitHub\HTML-to-PDF\app.py
```

### API not responding?

```bash
# Check container status
docker-compose ps

# Check if port is open
sudo netstat -tulpn | grep 5000

# Check nginx/reverse proxy
sudo systemctl status nginx
```

---

## 🔄 Rollback (If Needed)

```bash
cd ~/HTML-to-PDF
docker-compose down

# Restore from backup
cp ~/HTML-to-PDF-backups/LATEST/app.py ./
cp ~/HTML-to-PDF-backups/LATEST/requirements.txt ./

docker-compose up -d --build
```

---

## 📋 What Gets Updated

### Modified Files:
- ✅ `app.py` - Core improvements
- ✅ `requirements.txt` - Added Pillow

### New Files (Optional):
- 📄 `RENDERING_IMPROVEMENTS.md` - Full documentation
- 📄 `VPS_UPDATE_GUIDE.md` - This guide
- 📄 `examples/enhanced_usage_example.py` - Usage examples
- 📄 `test_improvements.py` - Test suite

---

## 🎯 Expected Result

After update, your API will support:

```json
{
  "html": "...",
  "css": "...",
  "filename": "output.pdf",
  "base_url": "https://example.com/",     // NEW ✨
  "page_size": "Letter",                  // NEW ✨
  "margin": "1in",                        // NEW ✨
  "optimize": true                        // NEW ✨
}
```

**Benefits:**
- 🎨 Better HTML rendering
- 🖼️ External images load properly
- 📄 Custom page sizes
- 📉 Smaller PDF files (20-40% reduction)
- 🔤 Better text quality
- 🌍 International characters work

---

## 📞 Need Help?

1. **Check logs:** `docker-compose logs -f`
2. **Check status:** `docker-compose ps`
3. **Test locally:** `curl http://localhost:5000/`
4. **Read docs:** `cat RENDERING_IMPROVEMENTS.md`

---

## ⏱️ Estimated Time

- **Method 1 (Script):** ~2-3 minutes
- **Method 2 (Git):** ~1-2 minutes  
- **Method 3 (Manual):** ~5 minutes

**Downtime:** ~30 seconds during container restart

---

**Ready? Pick a method above and start! 🚀**
