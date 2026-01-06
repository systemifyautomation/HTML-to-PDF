"""
Simple test of the Flask API endpoint with small HTML
"""
import requests
import json

# Test API key (from .api-keys.test.json)
API_KEY = "test-api-key-valid-12345678901234567890"

print("Testing Flask API endpoint with simple HTML...")

# Simple HTML content
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Test</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is a simple test PDF.</p>
    <p>Testing the Flask API with Playwright backend.</p>
</body>
</html>
"""

# Prepare the request payload
payload = {
    'html': html_content,
    'filename': 'simple_test.pdf',
    'page_size': 'A4',
    'margin': '10px'
}

try:
    # Send POST request to the Flask API
    print("Sending POST request to http://localhost:5000/convert...")
    response = requests.post(
        'http://localhost:5000/convert',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        },
        timeout=60  # Increased timeout
    )
    
    # Check response
    if response.status_code == 200:
        # Save the PDF
        with open('simple_test.pdf', 'wb') as f:
            f.write(response.content)
        print(f"✓ SUCCESS! PDF generated: {len(response.content)} bytes")
        print(f"  Saved as simple_test.pdf")
    else:
        print(f"✗ ERROR: HTTP {response.status_code}")
        print(f"  Response: {response.text}")
    
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Could not connect to Flask server")
    print("  Make sure the Flask server is running on port 5000")
    print("  Run: python app.py")
except requests.exceptions.Timeout:
    print("✗ ERROR: Request timed out (>60 seconds)")
    print("  The server may still be processing the request")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
