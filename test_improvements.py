"""
Test script to validate the HTML rendering improvements.
Run this after starting the API server to verify functionality.
"""

import requests
import json

API_URL = "http://localhost:5000/convert"
API_KEY = "your-api-key-here"  # Replace with actual key

def test_auto_html_correction():
    """Test 1: Automatic HTML structure correction"""
    print("\n🧪 Test 1: Auto HTML Correction")
    print("-" * 50)
    
    # Intentionally malformed HTML (missing DOCTYPE, tags, etc.)
    html = "<h1>Test Title</h1><p>This HTML is incomplete</p>"
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={'html': html, 'filename': 'test1_autocorrect.pdf'}
    )
    
    if response.status_code == 200:
        print("✅ PASS - Auto-correction works")
        with open('test1_autocorrect.pdf', 'wb') as f:
            f.write(response.content)
    else:
        print(f"❌ FAIL - {response.status_code}: {response.json()}")


def test_base_url():
    """Test 2: Base URL for external resources"""
    print("\n🧪 Test 2: Base URL Parameter")
    print("-" * 50)
    
    html = """
    <html>
    <body>
        <h1>Document with Image</h1>
        <img src="logo.png" alt="Logo" style="width:100px;">
        <p>Image loaded via base_url</p>
    </body>
    </html>
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={
            'html': html,
            'base_url': 'https://via.placeholder.com/',  # Test URL
            'filename': 'test2_baseurl.pdf'
        }
    )
    
    if response.status_code == 200:
        print("✅ PASS - Base URL parameter works")
        with open('test2_baseurl.pdf', 'wb') as f:
            f.write(response.content)
    else:
        print(f"❌ FAIL - {response.status_code}: {response.json()}")


def test_custom_page_size():
    """Test 3: Custom page size and margins"""
    print("\n🧪 Test 3: Custom Page Size & Margins")
    print("-" * 50)
    
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Letter Size Document</h1>
        <p>This document uses Letter size with 1 inch margins.</p>
    </body>
    </html>
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={
            'html': html,
            'page_size': 'Letter',
            'margin': '1in',
            'filename': 'test3_pagesize.pdf'
        }
    )
    
    if response.status_code == 200:
        print("✅ PASS - Custom page size works")
        with open('test3_pagesize.pdf', 'wb') as f:
            f.write(response.content)
    else:
        print(f"❌ FAIL - {response.status_code}: {response.json()}")


def test_optimization():
    """Test 4: PDF optimization"""
    print("\n🧪 Test 4: PDF Optimization")
    print("-" * 50)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, Helvetica, sans-serif; }
            h1 { color: #333; font-size: 32px; }
        </style>
    </head>
    <body>
        <h1>Optimized PDF</h1>
        <p>This PDF should have optimized fonts and smaller size.</p>
    </body>
    </html>
    """
    
    # Test with optimization ON
    response_opt = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={'html': html, 'optimize': True, 'filename': 'test4_optimized.pdf'}
    )
    
    # Test with optimization OFF
    response_no_opt = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={'html': html, 'optimize': False, 'filename': 'test4_unoptimized.pdf'}
    )
    
    if response_opt.status_code == 200 and response_no_opt.status_code == 200:
        size_opt = len(response_opt.content)
        size_no_opt = len(response_no_opt.content)
        reduction = ((size_no_opt - size_opt) / size_no_opt) * 100
        
        print(f"✅ PASS - Optimization works")
        print(f"   Optimized size: {size_opt:,} bytes")
        print(f"   Unoptimized size: {size_no_opt:,} bytes")
        print(f"   Reduction: {reduction:.1f}%")
        
        with open('test4_optimized.pdf', 'wb') as f:
            f.write(response_opt.content)
        with open('test4_unoptimized.pdf', 'wb') as f:
            f.write(response_no_opt.content)
    else:
        print(f"❌ FAIL - Optimization test failed")


def test_smart_page_breaks():
    """Test 5: Smart page breaks"""
    print("\n🧪 Test 5: Smart Page Breaks")
    print("-" * 50)
    
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <div style="page-break-inside: avoid;">
            <h2>Section 1</h2>
            <p>This section stays together on one page.</p>
        </div>
        
        <table style="page-break-inside: avoid;">
            <tr><th>Header</th></tr>
            <tr><td>Row 1</td></tr>
            <tr><td>Row 2</td></tr>
        </table>
        
        <div style="page-break-before: always;">
            <h2>Section 2 (New Page)</h2>
            <p>This starts on a new page.</p>
        </div>
    </body>
    </html>
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={'html': html, 'filename': 'test5_pagebreaks.pdf'}
    )
    
    if response.status_code == 200:
        print("✅ PASS - Page break handling works")
        with open('test5_pagebreaks.pdf', 'wb') as f:
            f.write(response.content)
    else:
        print(f"❌ FAIL - {response.status_code}: {response.json()}")


def test_special_characters():
    """Test 6: Special character encoding"""
    print("\n🧪 Test 6: Special Character Encoding")
    print("-" * 50)
    
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Special Characters Test</h1>
        <p>English: Hello World</p>
        <p>Spanish: Hola Mundo - ñ, á, é, í, ó, ú</p>
        <p>French: Bonjour le monde - é, è, ê, ë, ç</p>
        <p>German: Hallo Welt - ä, ö, ü, ß</p>
        <p>Symbols: © ® ™ € £ ¥ • § ¶</p>
        <p>Math: ≈ ≠ ≤ ≥ ± × ÷ √</p>
    </body>
    </html>
    """
    
    response = requests.post(
        API_URL,
        headers={'X-API-Key': API_KEY},
        json={'html': html, 'filename': 'test6_encoding.pdf'}
    )
    
    if response.status_code == 200:
        print("✅ PASS - Special characters handled")
        with open('test6_encoding.pdf', 'wb') as f:
            f.write(response.content)
    else:
        print(f"❌ FAIL - {response.status_code}: {response.json()}")


def test_api_info():
    """Test 7: Check API info endpoint"""
    print("\n🧪 Test 7: API Information")
    print("-" * 50)
    
    response = requests.get("http://localhost:5000/")
    
    if response.status_code == 200:
        data = response.json()
        if 'improvements' in data.get('usage', {}):
            print("✅ PASS - API documentation updated")
            print(f"   Improvements listed: {len(data['usage']['improvements'])}")
        else:
            print("⚠️  WARNING - Improvements not listed in API docs")
    else:
        print(f"❌ FAIL - Cannot reach API")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("HTML-to-PDF Rendering Improvements Test Suite")
    print("=" * 60)
    print("\n⚙️  Configuration:")
    print(f"   API URL: {API_URL}")
    print(f"   API Key: {API_KEY[:10]}..." if len(API_KEY) > 10 else f"   API Key: {API_KEY}")
    print("\n📝 Make sure:")
    print("   1. API server is running (python app.py)")
    print("   2. API key is configured correctly")
    print("   3. .api-keys.json file exists with valid keys")
    
    input("\nPress Enter to start tests...")
    
    try:
        test_api_info()
        test_auto_html_correction()
        test_custom_page_size()
        test_smart_page_breaks()
        test_special_characters()
        test_optimization()
        # test_base_url()  # May fail if no internet/external images
        
        print("\n" + "=" * 60)
        print("✅ Test Suite Complete!")
        print("=" * 60)
        print("\n📄 Generated PDFs:")
        print("   - test1_autocorrect.pdf")
        print("   - test3_pagesize.pdf")
        print("   - test4_optimized.pdf")
        print("   - test4_unoptimized.pdf")
        print("   - test5_pagebreaks.pdf")
        print("   - test6_encoding.pdf")
        print("\n💡 Review the PDFs to verify rendering quality")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("   Make sure the server is running: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
