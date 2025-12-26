# Clio File Upload Integration

This branch adds Python backend functionality for uploading files to Clio.com, a legal practice management software.

## 🎯 Features

- Upload files from your local PC to Clio
- Interactive file selection
- Attach files to specific matters in Clio
- List recent documents and matters
- Simple command-line interface
- Secure credential management

## 📋 Prerequisites

1. **Clio Account**: You need an active Clio account
2. **Developer Access**: Access to Clio's Developer Applications settings
3. **Python 3.8+**: Python installed on your system
4. **API Access Token**: OAuth2 access token from Clio

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
# Make sure you're in the project directory
cd HTML-to-PDF

# Create/activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies (including Clio library)
pip install -r requirements.txt
```

### Step 2: Get Your Clio Access Token

1. Log in to your Clio account at [https://app.clio.com](https://app.clio.com)
2. Navigate to **Settings** → **Developer Applications**
3. Create a new application or use an existing one
4. Generate an **Access Token** (OAuth2)
5. Copy the access token - you'll need it in the next step

### Step 3: Configure Clio Credentials

```bash
# Copy the example configuration file
cp .clio-config.example.json .clio-config.json

# Edit the configuration file
nano .clio-config.json
# OR
code .clio-config.json
```

Update `.clio-config.json` with your access token:

```json
{
  "access_token": "YOUR_ACTUAL_ACCESS_TOKEN_HERE",
  "api_region": "app.clio.com",
  "note": "Get your access token from https://app.clio.com/settings/developer_applications"
}
```

⚠️ **IMPORTANT**: Never commit `.clio-config.json` to git! It's already in `.gitignore`.

## 💡 Usage

### Interactive Mode (Recommended for Testing)

Simply run the script without arguments for an interactive experience:

```bash
python clio_upload.py
```

This will:
1. Connect to Clio API
2. Let you select a file from your current directory
3. Optionally attach it to a matter
4. Upload the file to Clio

### Command-Line Mode

Upload a specific file:

```bash
python clio_upload.py --file /path/to/document.pdf
```

Upload and attach to a specific matter:

```bash
python clio_upload.py --file document.pdf --matter 12345
```

Upload with a custom name:

```bash
python clio_upload.py --file report.pdf --name "Q4 Financial Report"
```

### List Operations

List recent documents:

```bash
python clio_upload.py --list-documents
```

List recent matters:

```bash
python clio_upload.py --list-matters
```

### Advanced Options

```bash
# Use a different config file
python clio_upload.py --config /path/to/config.json --file document.pdf

# Upload with all options
python clio_upload.py \
  --file /path/to/document.pdf \
  --matter 12345 \
  --name "Custom Document Name" \
  --config .clio-config.json
```

## 📖 Command Reference

| Option | Short | Description |
|--------|-------|-------------|
| `--file` | `-f` | Path to file to upload |
| `--matter` | `-m` | Matter ID to attach file to |
| `--name` | `-n` | Custom name for the file in Clio |
| `--config` | `-c` | Path to config file (default: `.clio-config.json`) |
| `--list-documents` | | List recent documents from Clio |
| `--list-matters` | | List recent matters from Clio |
| `--help` | `-h` | Show help message |

## 🔒 Security Notes

1. **Never commit** your `.clio-config.json` file - it contains sensitive credentials
2. The `.gitignore` file is already configured to exclude it
3. Use OAuth2 tokens with appropriate scopes (minimal required permissions)
4. Rotate your access tokens periodically
5. Store backup credentials securely (password manager recommended)

## 🧪 Testing Locally

1. **Test Connection**:
   ```bash
   python clio_upload.py --list-matters
   ```
   This should list your recent matters if authentication is working.

2. **Test File Upload**:
   Create a test file and upload it:
   ```bash
   echo "Test document" > test.txt
   python clio_upload.py --file test.txt
   ```

3. **Verify in Clio**:
   - Log in to Clio
   - Check your documents section
   - Verify the file was uploaded

## 🛠️ Troubleshooting

### Error: "clio-manage-api-client not installed"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Error: "Configuration file not found"

**Solution**: Create the config file
```bash
cp .clio-config.example.json .clio-config.json
# Then add your access token
```

### Error: "Invalid access token"

**Solutions**:
1. Verify your token in `.clio-config.json`
2. Generate a new token from Clio Developer Applications
3. Ensure the token has the correct permissions (scopes)

### Error: "Upload failed"

**Possible causes**:
1. File is too large (check Clio's file size limits)
2. Invalid matter ID
3. Network connectivity issues
4. Insufficient permissions on your Clio account

## 📚 Clio API Resources

- [Clio Developer Documentation](https://docs.developers.clio.com/)
- [Clio API V4 Reference](https://docs.developers.clio.com/api-reference/)
- [Python SDK on PyPI](https://pypi.org/project/clio-manage-api-client/)
- [GitHub: clio-api-python-client](https://github.com/unigrated-solutions/clio-api-python-client)

## 🚀 Next Steps: API Deployment

Once local testing is complete, this functionality can be:

1. **Integrated into the Flask API** (app.py)
   - Add new endpoint: `/upload-to-clio`
   - Accept file uploads via HTTP POST
   - Return upload status and Clio document ID

2. **Deploy as Separate Service**
   - Create standalone FastAPI/Flask service
   - Deploy to VPS/cloud
   - Use as microservice alongside HTML-to-PDF

3. **Add to Docker**
   - Update Dockerfile to include Clio dependencies
   - Deploy as containerized service

## 🤝 Contributing

When contributing to the Clio integration:

1. Never commit credentials or tokens
2. Test thoroughly with your Clio sandbox/test account
3. Document any API changes or new features
4. Follow the existing code style

## 📄 License

This integration follows the same MIT License as the main HTML-to-PDF project.

---

**Questions or Issues?** Open an issue on GitHub or check the Clio Developer Documentation.

**Happy uploading! 🎉**
