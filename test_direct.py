"""
Direct test of the Playwright conversion function
"""
from app import html_to_pdf_playwright

# Read the broken HTML file
with open('examples/simple_template.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print("Testing HTML to PDF conversion directly...")
print(f"HTML length: {len(html_content)} characters\n")

options = {
    'page_size': 'A4',
    'width': '600px',
    'margin': '0',
    'viewport_width': 1920,
    'viewport_height': 1080
}

try:
    pdf_bytes = html_to_pdf_playwright(html_content, options)
    print(f"✓ SUCCESS! PDF generated: {len(pdf_bytes)} bytes")
    
    # Save the PDF
    with open('test_direct_output.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print(f"  Saved as test_direct_output.pdf")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
