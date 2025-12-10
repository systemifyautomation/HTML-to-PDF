"""
HTML to PDF API - Usage Examples with Screenshot Mode
Demonstrates auto-sizing PDFs to match HTML content exactly
"""

import requests
import json

# API Configuration
API_URL = "https://htmltopdf.systemifyautomation.com/convert"
API_KEY = "your-api-key-here"  # Replace with your actual API key

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# ============================================================================
# Example 1: Screenshot Mode (Default) - Auto-sized to content
# ============================================================================
def screenshot_mode_example():
    """PDF sized exactly to the HTML content, like a screenshot"""
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .card {
                background: white;
                color: #333;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                max-width: 600px;
            }
            h1 { color: #667eea; margin-bottom: 20px; }
            .info { 
                background: #f0f0f0; 
                padding: 15px; 
                border-radius: 5px;
                margin: 15px 0;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎨 Screenshot Mode Example</h1>
            <p>This PDF will be sized <strong>exactly</strong> to this content.</p>
            <div class="info">
                <strong>Mode:</strong> page_size = "auto"<br>
                <strong>Margin:</strong> 0 (default)<br>
                <strong>Result:</strong> PDF dimensions match HTML content
            </div>
            <p>No extra pages, no white space - just the content!</p>
        </div>
    </body>
    </html>
    """
    
    data = {
        "html": html,
        "filename": "screenshot_mode.pdf",
        "page_size": "auto",  # Screenshot mode
        "margin": "0"
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        with open("screenshot_mode.pdf", "wb") as f:
            f.write(response.content)
        print("✅ Screenshot mode PDF created: screenshot_mode.pdf")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

# ============================================================================
# Example 2: Fixed Width Mode - Width set, height auto
# ============================================================================
def fixed_width_mode_example():
    """PDF with fixed width (like 1200px desktop view), height adjusts to content"""
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f5f5;
                padding: 0;
                margin: 0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 40px;
            }
            .header {
                background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
                color: white;
                padding: 40px;
                text-align: center;
                margin: -40px -40px 40px -40px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin: 30px 0;
            }
            .box {
                background: #f9f9f9;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📱 Fixed Width Mode</h1>
                <p>Desktop-like layout with responsive height</p>
            </div>
            
            <h2>Features Grid</h2>
            <div class="grid">
                <div class="box">
                    <h3>🚀 Fast</h3>
                    <p>Lightning speed</p>
                </div>
                <div class="box">
                    <h3>🔒 Secure</h3>
                    <p>Enterprise-grade</p>
                </div>
                <div class="box">
                    <h3>📊 Scalable</h3>
                    <p>Grows with you</p>
                </div>
            </div>
            
            <p>Width: 1200px | Height: Auto-adjusts to content</p>
        </div>
    </body>
    </html>
    """
    
    data = {
        "html": html,
        "filename": "fixed_width.pdf",
        "page_size": "auto",
        "width": "1200px",  # Fixed desktop width
        "margin": "0"
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        with open("fixed_width.pdf", "wb") as f:
            f.write(response.content)
        print("✅ Fixed width PDF created: fixed_width.pdf")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

# ============================================================================
# Example 3: Standard Document Mode - Traditional A4 format
# ============================================================================
def standard_document_mode():
    """Traditional A4 document with margins"""
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: 'Times New Roman', Times, serif;
                line-height: 1.8;
            }
            h1 {
                text-align: center;
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            .section {
                margin: 20px 0;
            }
            .footer {
                margin-top: 50px;
                text-align: center;
                font-size: 12px;
                color: #7f8c8d;
            }
        </style>
    </head>
    <body>
        <h1>Business Report</h1>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <p>This document demonstrates traditional A4 format with proper margins, 
            suitable for professional documents, reports, and letters.</p>
        </div>
        
        <div class="section">
            <h2>Key Findings</h2>
            <ul>
                <li>Professional A4 page size (210mm × 297mm)</li>
                <li>Standard 2cm margins on all sides</li>
                <li>Traditional document formatting</li>
                <li>Multi-page support with proper pagination</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Conclusion</h2>
            <p>Use this mode for formal documents that need to be printed 
            or follow standard document conventions.</p>
        </div>
        
        <div class="footer">
            Page 1 | Document Mode: A4 with 2cm margins
        </div>
    </body>
    </html>
    """
    
    data = {
        "html": html,
        "filename": "standard_document.pdf",
        "page_size": "A4",
        "margin": "2cm"
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        with open("standard_document.pdf", "wb") as f:
            f.write(response.content)
        print("✅ Standard document PDF created: standard_document.pdf")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

# ============================================================================
# Example 4: Mobile View Screenshot - Small width
# ============================================================================
def mobile_screenshot_example():
    """Mobile view screenshot - narrow width like a phone"""
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0;
                padding: 20px;
                background: #fff;
            }
            .mobile-header {
                background: #4CAF50;
                color: white;
                padding: 15px;
                margin: -20px -20px 20px -20px;
            }
            .card {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .button {
                background: #4CAF50;
                color: white;
                padding: 12px;
                text-align: center;
                border-radius: 5px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="mobile-header">
            <h2 style="margin: 0;">📱 Mobile App View</h2>
        </div>
        
        <div class="card">
            <h3>Notifications</h3>
            <p>You have 3 new messages</p>
        </div>
        
        <div class="card">
            <h3>Quick Actions</h3>
            <div class="button">Send Message</div>
            <div class="button">View Profile</div>
        </div>
        
        <div class="card">
            <h3>Settings</h3>
            <p>Configure your preferences</p>
        </div>
    </body>
    </html>
    """
    
    data = {
        "html": html,
        "filename": "mobile_screenshot.pdf",
        "page_size": "auto",
        "width": "375px",  # iPhone width
        "margin": "0"
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        with open("mobile_screenshot.pdf", "wb") as f:
            f.write(response.content)
        print("✅ Mobile screenshot PDF created: mobile_screenshot.pdf")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

# ============================================================================
# Run all examples
# ============================================================================
if __name__ == "__main__":
    print("🚀 HTML to PDF API - Screenshot Mode Examples\n")
    print("=" * 60)
    
    print("\n1. Screenshot Mode (Auto-sized to content)")
    screenshot_mode_example()
    
    print("\n2. Fixed Width Mode (1200px desktop view)")
    fixed_width_mode_example()
    
    print("\n3. Standard Document Mode (A4 with margins)")
    standard_document_mode()
    
    print("\n4. Mobile Screenshot (375px phone view)")
    mobile_screenshot_example()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("\nModes Summary:")
    print("  📸 Screenshot: Perfect for web content, dashboards, cards")
    print("  🖥️  Fixed Width: Desktop layouts, responsive designs")
    print("  📄 Standard Doc: Business reports, letters, formal docs")
    print("  📱 Mobile: App screenshots, phone layouts")
