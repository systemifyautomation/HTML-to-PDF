# Filename Feature Update Summary

## Version 2.1.0 - Enhanced Filename Support

### What's New

The `filename` parameter now includes **automatic security sanitization** to protect against path traversal and malicious filenames.

### Changes Made

#### 1. **Enhanced Security** ✅
- Auto-removes path separators (`../../`)
- Filters out dangerous characters (`<>|?*`)
- Only allows: letters, numbers, spaces, dots, hyphens, underscores
- Prevents directory traversal attacks

#### 2. **Smart Defaults** ✅
- Auto-adds `.pdf` extension if missing
- Defaults to `document.pdf` if empty
- Removes leading/trailing whitespace

#### 3. **Updated Documentation** 📚

**New Files:**
- `examples/FILENAME_GUIDE.md` - Complete guide with examples in Python, JavaScript, PHP
- `examples/README.md` - Examples directory overview

**Updated Files:**
- `README.md` - Added filename to core features, updated examples
- `app.py` - Enhanced sanitization, better docstrings
- `examples/usage_example.py` - Dynamic filename examples
- `PRODUCTION_DEPLOYMENT.md` - Updated for GitHub deployment
- `UPDATING.md` - Guide for updating from GitHub

### Usage Examples

#### Basic Usage
```python
response = requests.post(url, json={
    'html': '<h1>Invoice</h1>',
    'filename': 'invoice-12345.pdf'  # Custom filename
})
```

#### Dynamic Filenames
```python
# Date-based
filename = f"report-{datetime.now().strftime('%Y-%m-%d')}.pdf"

# Invoice numbers
filename = f"invoice-{invoice_id}.pdf"

# User-specific
filename = f"{user_id}-statement.pdf"
```

### Security Examples

| Input | Output | Notes |
|-------|--------|-------|
| `invoice 2024.pdf` | `invoice 2024.pdf` | ✅ Safe |
| `../../../etc/passwd` | `etcpasswd.pdf` | ✅ Sanitized |
| `file<script>.pdf` | `filescript.pdf` | ✅ Cleaned |
| `report` | `report.pdf` | ✅ Auto .pdf |

### Migration Guide

**No breaking changes!** The filename parameter works exactly as before, but now with added security.

If you're already using `filename`:
- ✅ Everything continues to work
- ✅ Added automatic security
- ✅ No code changes needed

### Testing

```bash
# Test with clean filename
curl -X POST https://your-domain.com/convert \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"html":"<h1>Test</h1>","filename":"invoice-123.pdf"}' \
  -o test.pdf

# Test with malicious filename (will be sanitized)
curl -X POST https://your-domain.com/convert \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"html":"<h1>Test</h1>","filename":"../../etc/passwd"}' \
  -o test.pdf
# Server returns: etcpasswd.pdf (sanitized)
```

### Documentation

- **Complete Guide**: [examples/FILENAME_GUIDE.md](examples/FILENAME_GUIDE.md)
- **API Docs**: [README.md#api-documentation](README.md#-api-documentation)
- **Examples**: [examples/usage_example.py](examples/usage_example.py)

### Benefits

1. **Security** 🔒
   - Prevents path traversal attacks
   - Protects against malicious filenames
   - Safe for production use

2. **Flexibility** 🎯
   - Dynamic invoice numbers
   - Date-based reports
   - User-specific documents
   - Custom naming patterns

3. **Reliability** ✅
   - Auto-corrects common mistakes
   - Handles edge cases
   - Always returns valid filename

### Deployment

After pulling this update:

```bash
# On your VPS
cd /opt/html-to-pdf
git pull origin main
systemctl restart html-to-pdf

# Verify version
curl http://localhost:5000/version
# Should show: "version": "2.1.0"
```

Or use the automated update script:
```bash
sudo /opt/html-to-pdf/deployment/update-from-github.sh
```

---

**Version**: 2.1.0  
**Date**: January 6, 2026  
**Commit**: Enhanced filename parameter with security sanitization
