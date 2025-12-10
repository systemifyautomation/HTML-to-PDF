#!/usr/bin/env python3
"""
API Key Generator for HTML-to-PDF API
Generates secure random API keys and manages .api-keys.json file
"""

import json
import secrets
import sys
from datetime import datetime
from pathlib import Path

def generate_api_key():
    """Generate a secure random API key."""
    return secrets.token_urlsafe(32)

def load_api_keys_file(file_path):
    """Load existing API keys file or create new structure."""
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "api_keys": [],
            "rate_limit": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000
            }
        }

def save_api_keys_file(file_path, data):
    """Save API keys to file with proper formatting."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    # Set restrictive permissions (Unix-like systems)
    try:
        file_path.chmod(0o600)  # Read/write for owner only
    except Exception:
        pass  # Windows doesn't support chmod the same way

def add_api_key(name, active=True):
    """Add a new API key to the configuration."""
    script_dir = Path(__file__).parent
    api_keys_file = script_dir / '.api-keys.json'
    
    # Load existing data
    data = load_api_keys_file(api_keys_file)
    
    # Generate new key
    new_key = generate_api_key()
    
    # Add to keys list
    data['api_keys'].append({
        "key": new_key,
        "name": name,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "active": active
    })
    
    # Save
    save_api_keys_file(api_keys_file, data)
    
    return new_key

def list_api_keys():
    """List all API keys (masked for security)."""
    script_dir = Path(__file__).parent
    api_keys_file = script_dir / '.api-keys.json'
    
    if not api_keys_file.exists():
        print("No API keys file found.")
        return
    
    data = load_api_keys_file(api_keys_file)
    
    print("\n=== API Keys ===")
    for idx, key_info in enumerate(data['api_keys'], 1):
        status = "✓ Active" if key_info.get('active') else "✗ Inactive"
        masked_key = key_info['key'][:8] + "..." + key_info['key'][-4:]
        print(f"{idx}. {key_info['name']}")
        print(f"   Key: {masked_key}")
        print(f"   Created: {key_info.get('created', 'Unknown')}")
        print(f"   Status: {status}\n")
    
    print("=== Rate Limits ===")
    rl = data.get('rate_limit', {})
    print(f"Per Minute: {rl.get('requests_per_minute', 'N/A')}")
    print(f"Per Hour: {rl.get('requests_per_hour', 'N/A')}")

def deactivate_key(key_prefix):
    """Deactivate an API key by its prefix."""
    script_dir = Path(__file__).parent
    api_keys_file = script_dir / '.api-keys.json'
    
    data = load_api_keys_file(api_keys_file)
    
    found = False
    for key_info in data['api_keys']:
        if key_info['key'].startswith(key_prefix):
            key_info['active'] = False
            found = True
            print(f"Deactivated key: {key_info['name']}")
    
    if found:
        save_api_keys_file(api_keys_file, data)
    else:
        print(f"No key found starting with: {key_prefix}")

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_api_key.py add <name>     - Generate new API key")
        print("  python generate_api_key.py list           - List all API keys")
        print("  python generate_api_key.py deactivate <prefix> - Deactivate a key")
        print("\nExamples:")
        print("  python generate_api_key.py add 'Production Server'")
        print("  python generate_api_key.py add 'Client A'")
        print("  python generate_api_key.py list")
        print("  python generate_api_key.py deactivate abc12345")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'add':
        if len(sys.argv) < 3:
            print("Error: Please provide a name for the API key")
            print("Usage: python generate_api_key.py add <name>")
            return
        
        name = ' '.join(sys.argv[2:])
        key = add_api_key(name)
        print(f"\n✓ Generated new API key for: {name}")
        print(f"\nAPI Key: {key}")
        print("\n⚠️  IMPORTANT: Save this key securely. It won't be displayed again in full.")
        print("Add this to your requests using the X-API-Key header.\n")
    
    elif command == 'list':
        list_api_keys()
    
    elif command == 'deactivate':
        if len(sys.argv) < 3:
            print("Error: Please provide the key prefix to deactivate")
            print("Usage: python generate_api_key.py deactivate <key_prefix>")
            return
        
        key_prefix = sys.argv[2]
        deactivate_key(key_prefix)
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: add, list, deactivate")

if __name__ == '__main__':
    main()
