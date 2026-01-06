"""
Test the Flask API endpoint for HTML to PDF conversion
"""
import requests
import json

# Read the HTML template
with open('examples/simple_template.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print("Testing Flask API endpoint...")
print(f"HTML length: {len(html_content)} characters\n")

# Prepare the request payload
payload = {
    'html': html_content,
    'filename': 'api_test_output.pdf',
    'page_size': 'A4',
    'margin': '0',
    'viewport_width': 1920,
    'viewport_height': 1080
}

try:
    # Send POST request to the Flask API
    print("Sending POST request to http://localhost:5000/convert...")
    response = requests.post(
        'http://localhost:5000/convert',
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=120  # Increased timeout for large HTML
    )
    
    # Check response
    if response.status_code == 200:
        # Save the PDF
        with open('api_test_output.pdf', 'wb') as f:
            f.write(response.content)
        print(f"✓ SUCCESS! PDF generated: {len(response.content)} bytes")
        print(f"  Saved as api_test_output.pdf")
    else:
        print(f"✗ ERROR: HTTP {response.status_code}")
        print(f"  Response: {response.text}")
    
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Could not connect to Flask server")
    print("  Make sure the Flask server is running on port 5000")
    print("  Run: python app.py")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
