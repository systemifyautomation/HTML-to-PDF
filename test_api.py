#!/usr/bin/env python3
"""
Test script to verify the HTML to PDF API functionality.
Run this after starting the API server to ensure everything works correctly.
"""

import requests
import sys
import time

API_BASE_URL = "http://localhost:5000"

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": "\033[92m✓\033[0m",
        "error": "\033[91m✗\033[0m",
        "info": "\033[94mℹ\033[0m",
        "warning": "\033[93m⚠\033[0m"
    }
    symbol = colors.get(status, colors["info"])
    print(f"{symbol} {message}")

def test_health_check():
    """Test 1: Health check endpoint"""
    print("\n--- Test 1: Health Check ---")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print_status("Health check passed", "success")
                return True
            else:
                print_status(f"Unexpected health status: {data}", "error")
                return False
        else:
            print_status(f"Health check failed with status {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Health check failed: {e}", "error")
        return False

def test_home_endpoint():
    """Test 2: Home/documentation endpoint"""
    print("\n--- Test 2: Home Endpoint ---")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            if "service" in data and "endpoints" in data:
                print_status("Home endpoint working correctly", "success")
                return True
            else:
                print_status("Home endpoint returned unexpected data", "error")
                return False
        else:
            print_status(f"Home endpoint failed with status {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Home endpoint test failed: {e}", "error")
        return False

def test_simple_conversion():
    """Test 3: Simple HTML to PDF conversion"""
    print("\n--- Test 3: Simple HTML Conversion ---")
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body><h1>Test Document</h1><p>This is a test.</p></body>
    </html>
    """
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/convert",
            json={"html": html, "filename": "test_simple.pdf"}
        )
        
        if response.status_code == 200:
            if response.headers.get("Content-Type") == "application/pdf":
                pdf_size = len(response.content)
                if pdf_size > 0:
                    print_status(f"PDF generated successfully ({pdf_size} bytes)", "success")
                    return True
                else:
                    print_status("PDF is empty", "error")
                    return False
            else:
                print_status("Response is not a PDF", "error")
                return False
        else:
            print_status(f"Conversion failed: {response.status_code} - {response.text}", "error")
            return False
    except Exception as e:
        print_status(f"Simple conversion test failed: {e}", "error")
        return False

def test_conversion_with_css():
    """Test 4: HTML to PDF with custom CSS"""
    print("\n--- Test 4: HTML with Custom CSS ---")
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <div class="header"><h1>Styled Document</h1></div>
        <p>This has custom styling.</p>
    </body>
    </html>
    """
    
    css = """
    .header { 
        background-color: #007bff; 
        color: white; 
        padding: 20px; 
    }
    """
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/convert",
            json={"html": html, "css": css, "filename": "test_styled.pdf"}
        )
        
        if response.status_code == 200:
            print_status("PDF with CSS generated successfully", "success")
            return True
        else:
            print_status(f"CSS conversion failed: {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"CSS conversion test failed: {e}", "error")
        return False

def test_missing_html():
    """Test 5: Error handling - missing HTML"""
    print("\n--- Test 5: Error Handling (Missing HTML) ---")
    try:
        response = requests.post(
            f"{API_BASE_URL}/convert",
            json={"filename": "test.pdf"}
        )
        
        if response.status_code == 400:
            print_status("Error handling works correctly", "success")
            return True
        else:
            print_status(f"Expected 400, got {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Error handling test failed: {e}", "error")
        return False

def test_invalid_json():
    """Test 6: Error handling - invalid JSON"""
    print("\n--- Test 6: Error Handling (Invalid JSON) ---")
    try:
        response = requests.post(
            f"{API_BASE_URL}/convert",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [400, 415]:
            print_status("Invalid JSON handled correctly", "success")
            return True
        else:
            print_status(f"Expected 400/415, got {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Invalid JSON test failed: {e}", "error")
        return False

def test_nonexistent_endpoint():
    """Test 7: 404 handling"""
    print("\n--- Test 7: 404 Handling ---")
    try:
        response = requests.get(f"{API_BASE_URL}/nonexistent")
        
        if response.status_code == 404:
            print_status("404 handling works correctly", "success")
            return True
        else:
            print_status(f"Expected 404, got {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"404 test failed: {e}", "error")
        return False

def check_api_availability():
    """Check if API is available"""
    print("Checking API availability...")
    for attempt in range(5):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print_status("API is available", "success")
                return True
        except:
            if attempt < 4:
                print_status(f"Waiting for API... (attempt {attempt + 1}/5)", "warning")
                time.sleep(2)
    
    print_status("API is not available. Please start the server first:", "error")
    print("  python app.py")
    return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("HTML to PDF API Test Suite")
    print("=" * 60)
    
    # Check if API is available
    if not check_api_availability():
        sys.exit(1)
    
    # Run all tests
    tests = [
        test_health_check,
        test_home_endpoint,
        test_simple_conversion,
        test_conversion_with_css,
        test_missing_html,
        test_invalid_json,
        test_nonexistent_endpoint
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print_status("All tests passed! 🎉", "success")
        sys.exit(0)
    else:
        print_status(f"{total - passed} test(s) failed", "error")
        sys.exit(1)

if __name__ == "__main__":
    main()
