"""
Quick test script to verify Playwright installation and HTML to PDF conversion.
"""

from playwright.sync_api import sync_playwright
import tempfile
import os

def test_playwright_pdf():
    """Test Playwright HTML to PDF conversion."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Document</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>Hello, World!</h1>
        <p>This is a test PDF generated with Playwright.</p>
        <p>If you can see this, Playwright is working correctly!</p>
    </body>
    </html>
    """
    
    temp_file = None
    
    try:
        with sync_playwright() as p:
            # Launch browser
            print("Launching Chromium...")
            browser = p.chromium.launch(headless=True)
            
            # Create page
            print("Creating page...")
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            # Write HTML to temp file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(html_content)
            temp_file.close()
            
            # Load HTML
            file_url = f"file:///{temp_file.name.replace(chr(92), '/')}"
            print(f"Loading HTML from: {file_url}")
            page.goto(file_url, wait_until='networkidle')
            
            # Generate PDF
            print("Generating PDF...")
            pdf_bytes = page.pdf(
                format='A4',
                print_background=True,
                margin={
                    'top': '0px',
                    'right': '0px',
                    'bottom': '0px',
                    'left': '0px'
                }
            )
            
            # Save PDF
            output_path = 'test_playwright_output.pdf'
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"\n✅ SUCCESS! PDF generated: {output_path}")
            print(f"   File size: {len(pdf_bytes)} bytes")
            
            # Close browser
            browser.close()
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass

if __name__ == '__main__':
    print("Testing Playwright HTML to PDF conversion...\n")
    test_playwright_pdf()
