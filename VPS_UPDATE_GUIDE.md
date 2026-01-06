# VPS Update Guide

> **Note:** This guide is for Docker-based deployments. For systemd deployments (recommended), see [Quick Update Guide](QUICK_UPDATE_GUIDE.md).

## 🚀 Quick Update - Systemd Deployment

**One-line update from Windows:**

```powershell
.\update-vps-simple.ps1 -Auto
```

See [QUICK_UPDATE_GUIDE.md](QUICK_UPDATE_GUIDE.md) for setup and details.

---

## Docker Deployment Updates

### Option 1: Git Pull Update (For Docker Deployments)

```bash
# SSH into your VPS
ssh your-user@htmltopdf.systemifyautomation.com

# Navigate to your app directory
cd ~/HTML-to-PDF

# Stop the running container
docker-compose down

# Pull the latest changes from GitHub
git pull origin main

# Rebuild and restart the container
docker-compose up -d --build

# Check if it's running
docker-compose ps

# View logs to verify
docker-compose logs -f
```

### Option 2: Manual File Update

If you haven't pushed to GitHub yet or want to update manually:

```bash
# SSH into your VPS
ssh your-user@htmltopdf.systemifyautomation.com

# Navigate to your app directory
cd ~/HTML-to-PDF

# Backup current version
cp app.py app.py.backup
cp requirements.txt requirements.txt.backup

# Stop the running container
docker-compose down
```

Then upload these files using SCP or SFTP:
- `app.py` (modified)
- `requirements.txt` (modified)
- `RENDERING_IMPROVEMENTS.md` (new)
- `IMPROVEMENTS_SUMMARY.md` (new)
- `examples/enhanced_usage_example.py` (new)
- `test_improvements.py` (new)

```bash
# After uploading, rebuild and restart
docker-compose up -d --build

# Check status
docker-compose ps
docker-compose logs -f
```

### Option 3: Direct File Transfer from Windows

From your Windows machine (PowerShell):

```powershell
# Set your VPS details
$VPS_USER = "your-username"
$VPS_HOST = "htmltopdf.systemifyautomation.com"
$VPS_PATH = "~/HTML-to-PDF"
$LOCAL_PATH = "C:\Users\PCZZ3\Documents\GitHub\HTML-to-PDF"

# Upload modified files using SCP
scp "$LOCAL_PATH\app.py" "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/app.py"
scp "$LOCAL_PATH\requirements.txt" "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/requirements.txt"
scp "$LOCAL_PATH\RENDERING_IMPROVEMENTS.md" "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/"
scp "$LOCAL_PATH\IMPROVEMENTS_SUMMARY.md" "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/"
scp "$LOCAL_PATH\examples\enhanced_usage_example.py" "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/examples/"
scp "$LOCAL_PATH\test_improvements.py" "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/"

# Then SSH and restart
ssh ${VPS_USER}@${VPS_HOST} "cd ${VPS_PATH} && docker-compose down && docker-compose up -d --build"
```

## 🔍 Verify the Update

After updating, verify everything is working:

```bash
# Check container status
docker-compose ps

# Check logs for any errors
docker-compose logs --tail=50

# Test the API
curl -X GET https://htmltopdf.systemifyautomation.com/

# You should see the new "improvements" field in the response
```

Expected response should include:
```json
{
  "improvements": [
    "Automatic HTML structure validation and correction",
    "Smart page break handling",
    ...
  ]
}
```

## 🧪 Test the New Features

```bash
# Test with new parameters
curl -X POST https://htmltopdf.systemifyautomation.com/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "html": "<h1>Test</h1><p>Testing new features</p>",
    "page_size": "Letter",
    "margin": "1in",
    "optimize": true,
    "filename": "test.pdf"
  }' \
  --output test.pdf
```

## 📊 Monitor After Deployment

```bash
# Watch logs in real-time
docker-compose logs -f

# Check resource usage
docker stats

# View recent errors (if any)
docker-compose logs | grep ERROR
```

## 🔄 Rollback (If Needed)

If something goes wrong:

```bash
# Stop new version
docker-compose down

# Restore backups
cp app.py.backup app.py
cp requirements.txt.backup requirements.txt

# Rebuild with old version
docker-compose up -d --build
```

## 📝 What Changed in the Deployment

### Modified Files:
- `app.py` - Enhanced with new rendering features
- `requirements.txt` - Added Pillow dependency

### New Files (Optional but Recommended):
- `RENDERING_IMPROVEMENTS.md` - Documentation
- `IMPROVEMENTS_SUMMARY.md` - Technical summary
- `examples/enhanced_usage_example.py` - Usage examples
- `test_improvements.py` - Test suite

### Docker Image Changes:
The Dockerfile already has all needed dependencies. The new `Pillow` package will be installed automatically during rebuild.

## ⚠️ Important Notes

1. **Zero Downtime**: Use `docker-compose up -d --build` to minimize downtime
2. **Backup First**: Always backup before updating
3. **Check Logs**: Monitor logs after deployment
4. **Test API**: Verify all endpoints work after update
5. **Backward Compatible**: All existing API calls will continue to work

## 🐛 Troubleshooting

### Container won't start:
```bash
docker-compose logs
# Check for Python syntax errors or missing dependencies
```

### Import errors:
```bash
# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use:
```bash
# Check what's using port 5000
sudo netstat -tulpn | grep 5000
# Or change port in docker-compose.yml
```

### Permission issues:
```bash
# Fix permissions
sudo chown -R $USER:$USER ~/HTML-to-PDF
chmod +x ~/HTML-to-PDF/app.py
```

## 📈 Expected Improvements

After this update, you'll have:
- ✅ Better HTML rendering (auto-correction)
- ✅ External resource loading (base_url)
- ✅ Custom page sizes and margins
- ✅ PDF optimization (smaller files)
- ✅ Smart page breaks
- ✅ Better typography
- ✅ Special character support

## 🔐 Security Note

Make sure your `.api-keys.json` file is present and secure:

```bash
# Check if API keys file exists
ls -la ~/HTML-to-PDF/.api-keys.json

# Ensure proper permissions (should be 600)
chmod 600 ~/HTML-to-PDF/.api-keys.json
```

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Verify all files uploaded correctly
3. Ensure `.api-keys.json` is present
4. Test API endpoint manually
5. Review `RENDERING_IMPROVEMENTS.md` for usage

---

**Ready to update?** Follow Option 1 (Git Pull) for the smoothest experience!
