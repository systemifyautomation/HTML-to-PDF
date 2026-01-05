"""
Test script to verify that broken HTML can be converted to PDF
"""
import requests
import json

# Read the broken HTML file
with open('examples/simple_template.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print("Testing HTML to PDF conversion with broken HTML...")
print(f"HTML length: {len(html_content)} characters")

# API endpoint (adjust if needed)
url = 'http://localhost:5000/convert'

# Prepare the request
payload = {
    'html': html_content,
    'filename': 'test_broken_html.pdf',
    'page_size': 'auto',
    'width': '600px',  # Email width
    'margin': '0'
}

headers = {
    'Content-Type': 'application/json'
}

# Add API key if you have one
# headers['X-API-Key'] = 'your-api-key-here'

try:
    print("\nSending request to API...")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        # Save the PDF
        with open('test_broken_html_output.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ SUCCESS! PDF generated and saved as 'test_broken_html_output.pdf'")
        print(f"  PDF size: {len(response.content)} bytes")
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(f"  Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Could not connect to the API server")
    print("  Make sure the server is running on http://localhost:5000")
except Exception as e:
    print(f"✗ ERROR: {str(e)}")
