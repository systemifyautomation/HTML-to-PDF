"""
Test the production API endpoint
"""
import requests
import json

# Read the broken HTML file
with open('examples/simple_template.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print("Testing PRODUCTION HTML to PDF endpoint...")
print(f"HTML length: {len(html_content)} characters\n")

# Production API endpoint
url = 'https://htmltopdf.systemifyautomation.com/convert'

# Prepare the request
payload = {
    'html': html_content,
    'filename': 'test_production.pdf',
    'page_size': 'A4',
    'width': '600px',
    'margin': '0'
}

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 't75OZ8oN9joTQ3d-P1-phM-shX3SOYy_VMlU9oojV34'
}

try:
    print("Sending request to production API...")
    print(f"URL: {url}\n")
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        # Save the PDF
        output_file = 'test_production_output.pdf'
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"✓ SUCCESS! PDF generated and saved as '{output_file}'")
        print(f"  PDF size: {len(response.content)} bytes")
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(f"  Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("✗ ERROR: Request timed out after 30 seconds")
except requests.exceptions.ConnectionError as e:
    print(f"✗ ERROR: Could not connect to server")
    print(f"  {e}")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
