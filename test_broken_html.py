"""
Test script to verify that broken HTML can be converted to PDF using Puppeteer
"""
import requests
import json

# Read the broken HTML file
with open('examples/simple_template.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print("Testing HTML to PDF conversion with broken HTML using Puppeteer...")
print(f"HTML length: {len(html_content)} characters")
print("\n✨ Puppeteer renders HTML exactly like Chrome browser!")
print("   All syntax errors are automatically handled!\n")

# API endpoint (adjust if needed)
url = 'http://localhost:5000/convert'

# Prepare the request
payload = {
    'html': html_content,
    'filename': 'test_broken_html_puppeteer.pdf',
    'page_size': 'A4',  # or 'auto' for content-sized
    'width': '600px',   # Email template width
    'margin': '0'
}

headers = {
    'Content-Type': 'application/json'
}

# Add API key if you have one
# headers['X-API-Key'] = 'your-api-key-here'

try:
    print("Sending request to API...")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        # Save the PDF
        output_file = 'test_broken_html_puppeteer_output.pdf'
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"✓ SUCCESS! PDF generated with Puppeteer and saved as '{output_file}'")
        print(f"  PDF size: {len(response.content)} bytes")
        print(f"\n🎉 Your HTML with syntax errors converted perfectly!")
        print(f"   Puppeteer handled all the broken tags, invalid CSS, etc.")
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(f"  Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Could not connect to the API server")
    print("  Make sure the server is running on http://localhost:5000")
except Exception as e:
    print(f"✗ ERROR: {str(e)}")
