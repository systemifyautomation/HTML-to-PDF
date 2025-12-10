"""
Enhanced usage examples for the HTML to PDF API.
Demonstrates new features for better HTML rendering.
"""

import requests
import json
from pathlib import Path

# API Configuration
API_URL = "http://localhost:5000/convert"
API_KEY = "your-api-key-here"  # Replace with your actual API key

def example_basic_conversion():
    """Basic HTML to PDF conversion with improvements."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Basic Document</title>
        <style>
            body { font-family: Arial, sans-serif; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Hello World</h1>
        <p>This is a basic PDF document with automatic optimizations.</p>
    </body>
    </html>
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={
            'html': html_content,
            'filename': 'basic_document.pdf'
        }
    )
    
    if response.status_code == 200:
        with open('basic_document.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Basic document created: basic_document.pdf")
    else:
        print(f"✗ Error: {response.json()}")


def example_with_external_resources():
    """Convert HTML with external images and stylesheets."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document with External Resources</title>
        <link rel="stylesheet" href="styles/main.css">
    </head>
    <body>
        <h1>Document with Images</h1>
        <img src="images/logo.png" alt="Logo">
        <p>External resources are loaded using base_url parameter.</p>
    </body>
    </html>
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={
            'html': html_content,
            'filename': 'with_resources.pdf',
            'base_url': 'https://example.com/'  # Base URL for resolving relative paths
        }
    )
    
    if response.status_code == 200:
        with open('with_resources.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Document with resources created: with_resources.pdf")
    else:
        print(f"✗ Error: {response.json()}")


def example_custom_page_size():
    """Create PDF with custom page size and margins."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Custom Page Size</h1>
        <p>This document uses Letter size with 1 inch margins.</p>
    </body>
    </html>
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={
            'html': html_content,
            'filename': 'custom_page.pdf',
            'page_size': 'Letter',  # Options: A4, A3, Letter, Legal, etc.
            'margin': '1in'  # Can use cm, in, mm, etc.
        }
    )
    
    if response.status_code == 200:
        with open('custom_page.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Custom page document created: custom_page.pdf")
    else:
        print(f"✗ Error: {response.json()}")


def example_complex_layout():
    """Convert complex HTML with tables, images, and proper page breaks."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Complex Layout</title>
        <style>
            body {
                font-family: 'Georgia', serif;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th {
                background-color: #3498db;
                color: white;
                padding: 12px;
                text-align: left;
            }
            td {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            .page-break {
                page-break-after: always;
            }
            .no-break {
                page-break-inside: avoid;
            }
        </style>
    </head>
    <body>
        <h1>Annual Report 2024</h1>
        
        <div class="no-break">
            <h2>Executive Summary</h2>
            <p>This section will not break across pages.</p>
        </div>
        
        <table class="no-break">
            <thead>
                <tr>
                    <th>Quarter</th>
                    <th>Revenue</th>
                    <th>Growth</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Q1 2024</td>
                    <td>$1.2M</td>
                    <td>15%</td>
                </tr>
                <tr>
                    <td>Q2 2024</td>
                    <td>$1.5M</td>
                    <td>25%</td>
                </tr>
            </tbody>
        </table>
        
        <div class="page-break"></div>
        
        <h2>Detailed Analysis</h2>
        <p>This content starts on a new page.</p>
    </body>
    </html>
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={
            'html': html_content,
            'filename': 'complex_layout.pdf',
            'optimize': True  # Enable optimization for smaller file size
        }
    )
    
    if response.status_code == 200:
        with open('complex_layout.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Complex layout document created: complex_layout.pdf")
    else:
        print(f"✗ Error: {response.json()}")


def example_with_custom_css():
    """Convert HTML with extensive custom CSS."""
    
    html_content = """
    <h1>Styled Document</h1>
    <p>This document has custom styling.</p>
    <div class="highlight">Important information here!</div>
    """
    
    custom_css = """
    body {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        background-color: #f5f5f5;
        padding: 20px;
    }
    h1 {
        color: #e74c3c;
        text-transform: uppercase;
    }
    .highlight {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 20px 0;
    }
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={
            'html': html_content,
            'css': custom_css,
            'filename': 'custom_styled.pdf'
        }
    )
    
    if response.status_code == 200:
        with open('custom_styled.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Custom styled document created: custom_styled.pdf")
    else:
        print(f"✗ Error: {response.json()}")


def example_malformed_html():
    """Demonstrate automatic HTML correction."""
    
    # This HTML is missing proper structure - the API will fix it
    html_content = """
    <h1>This HTML is incomplete</h1>
    <p>Missing DOCTYPE, html, head, and body tags!</p>
    <p>The API will automatically add them.</p>
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={
            'html': html_content,
            'filename': 'auto_corrected.pdf'
        }
    )
    
    if response.status_code == 200:
        with open('auto_corrected.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Auto-corrected document created: auto_corrected.pdf")
    else:
        print(f"✗ Error: {response.json()}")


if __name__ == '__main__':
    print("HTML to PDF API - Enhanced Usage Examples")
    print("=" * 50)
    print()
    
    # Run examples
    example_basic_conversion()
    example_with_external_resources()
    example_custom_page_size()
    example_complex_layout()
    example_with_custom_css()
    example_malformed_html()
    
    print()
    print("All examples completed!")
    print()
    print("New features used:")
    print("  ✓ Automatic HTML structure validation")
    print("  ✓ Smart page break handling")
    print("  ✓ External resource loading (base_url)")
    print("  ✓ Custom page sizes and margins")
    print("  ✓ PDF optimization")
    print("  ✓ Better typography and rendering")
