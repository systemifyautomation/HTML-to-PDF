# API Key Management

This document explains how to manage API keys for the HTML-to-PDF Converter API.

## 🔐 Security Overview

The API uses a multi-key authentication system with:
- ✅ Multiple active API keys support
- ✅ Key activation/deactivation without deletion
- ✅ Rate limiting per key
- ✅ Keys stored in `.api-keys.json` (never committed to Git)
- ✅ Secure random key generation

## 📁 Files

- **`.api-keys.json`** - Active keys file (NEVER commit to Git)
- **`.api-keys.example.json`** - Template file (committed to Git)
- **`generate_api_key.py`** - Key management script

## 🔑 Managing API Keys

### Generate a New API Key

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Generate key
python generate_api_key.py add "Production Server"
python generate_api_key.py add "Client A"
python generate_api_key.py add "Development"
```

Output:
```
✓ Generated new API key for: Production Server

API Key: aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890AbCdEfGh

⚠️  IMPORTANT: Save this key securely. It won't be displayed again in full.
```

### List All API Keys

```bash
python generate_api_key.py list
```

Output:
```
=== API Keys ===
1. Production Server
   Key: aBcDeFgH...EfGh
   Created: 2025-12-10
   Status: ✓ Active

2. Client A
   Key: xYz12345...9876
   Created: 2025-12-10
   Status: ✗ Inactive

=== Rate Limits ===
Per Minute: 60
Per Hour: 1000
```

### Deactivate an API Key

```bash
# Use the first 8 characters of the key
python generate_api_key.py deactivate aBcDeFgH
```

## 📋 Manual Configuration

### Create `.api-keys.json`

```bash
# Copy example file
cp .api-keys.example.json .api-keys.json

# Edit with your keys
nano .api-keys.json
```

### File Structure

```json
{
  "api_keys": [
    {
      "key": "your-secure-api-key-here",
      "name": "Production Key",
      "created": "2025-12-10",
      "active": true
    },
    {
      "key": "another-secure-key",
      "name": "Client A",
      "created": "2025-12-10",
      "active": false
    }
  ],
  "rate_limit": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000
  }
}
```

### Generate Keys Manually

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

## 🚀 Deployment

### On Your VPS

1. **Generate keys on the server:**
```bash
cd ~/HTML-to-PDF
source venv/bin/activate
python generate_api_key.py add "Production Key 1"
```

2. **Restart the service:**
```bash
sudo systemctl restart htmltopdf
```

3. **Verify:**
```bash
# Check logs for key loading
sudo journalctl -u htmltopdf -n 20
```

## 🔒 Security Best Practices

### DO:
✅ Use the `generate_api_key.py` script for secure random keys  
✅ Keep `.api-keys.json` file permissions restrictive (`chmod 600`)  
✅ Use different keys for different clients/services  
✅ Deactivate keys instead of deleting (for audit trail)  
✅ Regularly rotate keys  
✅ Monitor rate limit alerts in logs  

### DON'T:
❌ Never commit `.api-keys.json` to Git  
❌ Don't share keys in plain text (use secure channels)  
❌ Don't use simple/guessable keys  
❌ Don't keep inactive keys active  
❌ Don't share the same key across multiple clients  

## 📊 Rate Limiting

Default limits (configurable in `.api-keys.json`):
- **60 requests per minute** per API key
- **1000 requests per hour** per API key

### Adjust Rate Limits

Edit `.api-keys.json`:
```json
{
  "rate_limit": {
    "requests_per_minute": 120,
    "requests_per_hour": 5000
  }
}
```

Restart the service:
```bash
sudo systemctl restart htmltopdf
```

## 🧪 Testing

### Test with valid key:
```bash
curl -X POST https://htmltopdf.systemifyautomation.com/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"html": "<h1>Test</h1>"}' \
  --output test.pdf
```

### Test without key (should fail):
```bash
curl https://htmltopdf.systemifyautomation.com/convert
# Returns: 401 Unauthorized
```

### Test with invalid key (should fail):
```bash
curl -H "X-API-Key: invalid-key" https://htmltopdf.systemifyautomation.com/convert
# Returns: 403 Forbidden
```

### Test rate limiting:
```bash
# Run many requests quickly
for i in {1..70}; do
  curl -H "X-API-Key: your-key" https://htmltopdf.systemifyautomation.com/health
done
# Should hit rate limit after 60 requests
```

## 📝 Monitoring

### View authentication logs:
```bash
sudo journalctl -u htmltopdf -f | grep -i "api\|auth\|rate"
```

### Check for failed attempts:
```bash
sudo journalctl -u htmltopdf | grep "Invalid API key"
```

## 🔄 Key Rotation

Recommended rotation schedule: Every 90 days

1. Generate new key
2. Update clients with new key
3. Deactivate old key after grace period
4. Monitor logs to ensure all clients updated

```bash
# Generate new key
python generate_api_key.py add "Production Key 2"

# After grace period, deactivate old key
python generate_api_key.py deactivate <old-key-prefix>
```
