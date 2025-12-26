# Quick Start: Clio File Upload

This guide will get you up and running with Clio file uploads in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- Clio account with API access
- Active Clio access token

## 1. Installation (1 minute)

```bash
# Install dependencies
pip install -r requirements.txt
```

## 2. Configuration (2 minutes)

### Get Your Clio Access Token

1. Visit [https://app.clio.com/settings/developer_applications](https://app.clio.com/settings/developer_applications)
2. Create a new application or use existing
3. Generate an access token
4. Copy the token

### Configure the Script

```bash
# Copy the example config
cp .clio-config.example.json .clio-config.json

# Edit and add your token
nano .clio-config.json
```

Update the file:
```json
{
  "access_token": "paste-your-token-here",
  "api_region": "app.clio.com"
}
```

## 3. Test Connection (30 seconds)

```bash
# List your matters to verify connection
python clio_upload.py --list-matters
```

If you see your matters listed, you're connected! ✅

## 4. Upload Your First File (30 seconds)

```bash
# Create a test file
echo "Test document" > test.txt

# Upload it
python clio_upload.py --file test.txt
```

## 5. Interactive Mode (1 minute)

```bash
# Run without arguments for interactive mode
python clio_upload.py
```

Follow the prompts to:
- Select a file
- Choose whether to attach to a matter
- Confirm and upload

## Common Commands

```bash
# Upload a specific file
python clio_upload.py --file document.pdf

# Upload and attach to matter
python clio_upload.py --file invoice.pdf --matter 12345

# Upload with custom name
python clio_upload.py --file report.pdf --name "Q4 Report"

# List recent documents
python clio_upload.py --list-documents

# List matters
python clio_upload.py --list-matters
```

## Troubleshooting

### "Configuration file not found"
Run: `cp .clio-config.example.json .clio-config.json`

### "Invalid access token"
- Verify token in `.clio-config.json`
- Generate new token from Clio
- Check token has proper permissions

### "clio-manage-api-client not installed"
Run: `pip install -r requirements.txt`

## Next Steps

- 📖 Read [CLIO_UPLOAD_README.md](CLIO_UPLOAD_README.md) for detailed documentation
- 🔧 See [examples/clio_upload_examples.py](examples/clio_upload_examples.py) for integration examples
- 🚀 Integrate with HTML-to-PDF API workflow

## Security Note

⚠️ Never commit `.clio-config.json` - it's already in `.gitignore`

## Need Help?

- Check the full documentation: [CLIO_UPLOAD_README.md](CLIO_UPLOAD_README.md)
- Review examples: `python examples/clio_upload_examples.py`
- Clio API docs: [https://docs.developers.clio.com/](https://docs.developers.clio.com/)

---

**You're ready to go! 🎉**
