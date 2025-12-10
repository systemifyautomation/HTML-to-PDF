# Admin API Documentation

Complete guide for managing API keys via HTTP requests using the super-user token.

## 🔐 Super User Authentication

All admin endpoints require the super user key in the `X-Super-User-Key` header.

### Setting Up Super User

1. **Generate a secure super user key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Add to `.api-keys.json`:**
```json
{
  "super_user": {
    "key": "your-generated-super-user-key",
    "name": "Super Admin",
    "created": "2025-12-10",
    "note": "Full admin access"
  },
  "api_keys": [...]
}
```

3. **Restart the service:**
```bash
sudo systemctl restart htmltopdf
```

## 📋 Admin Endpoints

Base URL: `https://htmltopdf.systemifyautomation.com`

### 1. List All API Keys

**GET** `/admin/keys`

Lists all API keys with masked values for security.

**Headers:**
```
X-Super-User-Key: your-super-user-key
```

**Response:**
```json
{
  "success": true,
  "keys": [
    {
      "name": "Production Key",
      "key_preview": "aBcDeFgH...XyZ1",
      "created": "2025-12-10",
      "active": true
    }
  ],
  "total": 3,
  "rate_limit": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000
  }
}
```

**cURL Example:**
```bash
curl -X GET https://htmltopdf.systemifyautomation.com/admin/keys \
  -H "X-Super-User-Key: your-super-user-key"
```

---

### 2. Create New API Key

**POST** `/admin/keys`

Generates a new secure API key.

**Headers:**
```
Content-Type: application/json
X-Super-User-Key: your-super-user-key
```

**Body:**
```json
{
  "name": "Client A",
  "active": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "API key created successfully",
  "key": "aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890",
  "name": "Client A",
  "active": true,
  "warning": "Save this key securely. It will not be shown again in full."
}
```

**cURL Example:**
```bash
curl -X POST https://htmltopdf.systemifyautomation.com/admin/keys \
  -H "Content-Type: application/json" \
  -H "X-Super-User-Key: your-super-user-key" \
  -d '{
    "name": "Client A",
    "active": true
  }'
```

---

### 3. Update API Key (Activate/Deactivate)

**PATCH** `/admin/keys/<key_prefix>`

Update an existing API key's status or name.

**Headers:**
```
Content-Type: application/json
X-Super-User-Key: your-super-user-key
```

**Body:**
```json
{
  "active": false,
  "name": "Client A - Inactive"
}
```

**Response:**
```json
{
  "success": true,
  "message": "API key updated successfully"
}
```

**cURL Examples:**

Deactivate a key:
```bash
curl -X PATCH https://htmltopdf.systemifyautomation.com/admin/keys/aBcDeFgH \
  -H "Content-Type: application/json" \
  -H "X-Super-User-Key: your-super-user-key" \
  -d '{"active": false}'
```

Rename a key:
```bash
curl -X PATCH https://htmltopdf.systemifyautomation.com/admin/keys/aBcDeFgH \
  -H "Content-Type: application/json" \
  -H "X-Super-User-Key: your-super-user-key" \
  -d '{"name": "New Client Name"}'
```

Reactivate a key:
```bash
curl -X PATCH https://htmltopdf.systemifyautomation.com/admin/keys/aBcDeFgH \
  -H "Content-Type: application/json" \
  -H "X-Super-User-Key: your-super-user-key" \
  -d '{"active": true}'
```

---

### 4. Delete API Key

**DELETE** `/admin/keys/<key_prefix>`

Permanently delete an API key.

**Headers:**
```
X-Super-User-Key: your-super-user-key
```

**Response:**
```json
{
  "success": true,
  "message": "API key deleted successfully"
}
```

**cURL Example:**
```bash
curl -X DELETE https://htmltopdf.systemifyautomation.com/admin/keys/aBcDeFgH \
  -H "X-Super-User-Key: your-super-user-key"
```

---

## 🐍 Python Examples

### List All Keys
```python
import requests

response = requests.get(
    'https://htmltopdf.systemifyautomation.com/admin/keys',
    headers={'X-Super-User-Key': 'your-super-user-key'}
)

data = response.json()
print(f"Total keys: {data['total']}")
for key in data['keys']:
    print(f"{key['name']}: {key['key_preview']} - {'Active' if key['active'] else 'Inactive'}")
```

### Create New Key
```python
import requests

response = requests.post(
    'https://htmltopdf.systemifyautomation.com/admin/keys',
    headers={
        'Content-Type': 'application/json',
        'X-Super-User-Key': 'your-super-user-key'
    },
    json={
        'name': 'New Client',
        'active': True
    }
)

data = response.json()
if data['success']:
    print(f"✓ Created key: {data['key']}")
    print(f"⚠️  {data['warning']}")
```

### Deactivate Key
```python
import requests

key_prefix = 'aBcDeFgH'  # First 8 chars of the key

response = requests.patch(
    f'https://htmltopdf.systemifyautomation.com/admin/keys/{key_prefix}',
    headers={
        'Content-Type': 'application/json',
        'X-Super-User-Key': 'your-super-user-key'
    },
    json={'active': False}
)

if response.json()['success']:
    print("✓ Key deactivated")
```

### Delete Key
```python
import requests

key_prefix = 'aBcDeFgH'

response = requests.delete(
    f'https://htmltopdf.systemifyautomation.com/admin/keys/{key_prefix}',
    headers={'X-Super-User-Key': 'your-super-user-key'}
)

if response.json()['success']:
    print("✓ Key deleted permanently")
```

---

## 🔒 Security Best Practices

### Super User Key:
- ⚠️ **NEVER share or commit the super user key**
- ⚠️ Store it securely (password manager, encrypted vault)
- ⚠️ Rotate it regularly (every 90 days)
- ⚠️ Use HTTPS only for all admin operations
- ⚠️ Monitor logs for unauthorized admin access attempts

### Admin Operations:
- ✅ Only perform admin operations from trusted networks
- ✅ Use deactivation instead of deletion when possible (audit trail)
- ✅ Log all admin operations
- ✅ Review active keys regularly
- ✅ Remove keys for terminated clients immediately

---

## 🚨 Error Responses

### 401 Unauthorized
```json
{
  "error": "Admin authentication required",
  "message": "Please provide X-Super-User-Key header"
}
```

### 403 Forbidden
```json
{
  "error": "Invalid super user key",
  "message": "The provided super user key is not valid"
}
```

### 404 Not Found
```json
{
  "error": "No key found with prefix: aBcDeFgH"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to create key: [error details]"
}
```

---

## 📊 Monitoring Admin Activity

Check logs for admin operations:

```bash
# View all admin activity
sudo journalctl -u htmltopdf | grep "Super user\|admin"

# Monitor in real-time
sudo journalctl -u htmltopdf -f | grep -i admin

# Check for failed admin attempts
sudo journalctl -u htmltopdf | grep "Invalid super user"
```

---

## 🔄 Complete Workflow Example

### 1. Create a new client key
```bash
curl -X POST https://htmltopdf.systemifyautomation.com/admin/keys \
  -H "Content-Type: application/json" \
  -H "X-Super-User-Key: YOUR_SUPER_KEY" \
  -d '{"name": "Client XYZ", "active": true}'
```

### 2. Share key with client securely
Send the generated key to the client via secure channel.

### 3. Client uses the key
Client includes `X-API-Key` header in their requests.

### 4. Monitor usage
Check logs for the client's requests.

### 5. Deactivate when needed
```bash
curl -X PATCH https://htmltopdf.systemifyautomation.com/admin/keys/abc12345 \
  -H "Content-Type: application/json" \
  -H "X-Super-User-Key: YOUR_SUPER_KEY" \
  -d '{"active": false}'
```

### 6. Delete if no longer needed
```bash
curl -X DELETE https://htmltopdf.systemifyautomation.com/admin/keys/abc12345 \
  -H "X-Super-User-Key: YOUR_SUPER_KEY"
```

---

## 📞 Support

For security issues or questions about admin API:
- Check logs: `sudo journalctl -u htmltopdf`
- Review `.api-keys.json` file permissions
- Ensure super user key is properly configured
