#!/usr/bin/env python3
"""
Example script demonstrating how to use the HTML to PDF API.
This script sends various requests to the API and saves the generated PDFs.
"""

import requests
import os

# API endpoint
API_URL = "http://localhost:5000/convert"

def convert_html_to_pdf(html_content, css_content=None, filename="output.pdf", output_filename=None):
    """
    Send HTML content to the API and save the resulting PDF.
    
    Args:
        html_content (str): HTML content to convert
        css_content (str, optional): Additional CSS styles
        filename (str): Name for the downloaded PDF (sent to API, controls Content-Disposition header)
        output_filename (str, optional): Local filename to save as (defaults to filename)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if output_filename is None:
        output_filename = filename
    # Prepare the request payload
    payload = {
        "html": html_content,
        "filename": filename
    }
    
    if css_content:
        payload["css"] = css_content
    
    try:
        # Send POST request to the API
        response = requests.post(
            API_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if request was successful
        if response.status_code == 200:
            # Save the PDF file
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print(f"✓ PDF saved successfully: {output_filename}")
            if output_filename != filename:
                print(f"  (Server filename: {filename})")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False

def example_simple_html():
    """Example 1: Convert simple HTML to PDF"""
    print("\n--- Example 1: Simple HTML ---")
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Example</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
        <p>This is a simple HTML to PDF conversion example.</p>
    </body>
    </html>
    """
    convert_html_to_pdf(html, filename="example_simple.pdf")

def example_with_css():
    """Example 2: Convert HTML with custom CSS to PDF"""
    print("\n--- Example 2: HTML with Custom CSS ---")
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Styled Example</title>
    </head>
    <body>
        <div class="header">
            <h1>Styled Document</h1>
        </div>
        <div class="content">
            <p>This document has custom styling applied.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    css = """
    body {
        font-family: 'Helvetica', sans-serif;
        margin: 40px;
    }
    .header {
        background-color: #4CAF50;
        color: white;
        padding: 20px;
        text-align: center;
    }
    .content {
        margin-top: 30px;
        line-height: 1.8;
    }
    ul {
        background-color: #f0f0f0;
        padding: 20px;
    }
    """
    convert_html_to_pdf(html, css, filename="example_styled.pdf")

def example_from_file():
    """Example 3: Convert HTML from a template file"""
    print("\n--- Example 3: HTML from Template File ---")
    
    # Check if examples directory exists
    template_path = "examples/simple_template.html"
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            html = f.read()
        convert_html_to_pdf(html, filename="example_from_file.pdf")
    else:
        print(f"✗ Template file not found: {template_path}")

def example_invoice():
    """Example 4: Convert invoice template to PDF with dynamic filename"""
    print("\n--- Example 4: Invoice Template ---")
    
    template_path = "examples/invoice_template.html"
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            html = f.read()
        
        # Use dynamic filename based on invoice number
        invoice_number = "INV-2024-001"
        convert_html_to_pdf(html, filename=f"invoice-{invoice_number}.pdf")
    else:
        print(f"✗ Template file not found: {template_path}")

def example_report():
    """Example 5: Convert report template to PDF with date-based filename"""
    print("\n--- Example 5: Report Template ---")
    
    template_path = "examples/report_template.html"
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            html = f.read()
        
        # Use current date in filename
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        convert_html_to_pdf(html, filename=f"monthly-report-{date_str}.pdf")
    else:
        print(f"✗ Template file not found: {template_path}")

def check_api_health():
    """Check if the API is running and healthy"""
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✓ API is healthy and running")
            return True
        else:
            print("✗ API returned unexpected status")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to API: {e}")
        print("  Make sure the API is running: python app.py")
        return False

def main():
    """Run all examples"""
    print("=" * 50)
    print("HTML to PDF Conversion Examples")
    print("=" * 50)
    
    # Check API health
    if not check_api_health():
        return
    
    # Run all examples
    example_simple_html()
    example_with_css()
    example_from_file()
    example_invoice()
    example_report()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
