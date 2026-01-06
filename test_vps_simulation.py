"""
Comprehensive Production-Like Test Suite for HTML-to-PDF API
Tests authentication, authorization, rate limiting, and all API endpoints
Simulates VPS deployment environment
"""

import requests
import json
import time
from typing import Dict, Optional
import sys

# Test configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 60

# Test API keys (from .api-keys.test.json)
VALID_API_KEY = "test-api-key-valid-12345678901234567890"
INACTIVE_API_KEY = "test-api-key-inactive-12345678901234567890"
RATELIMIT_API_KEY = "test-api-key-ratelimit-12345678901234567890"
INVALID_API_KEY = "invalid-key-that-does-not-exist"
SUPER_USER_KEY = "test-super-user-key-12345678901234567890"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

def test_result(test_name: str, passed: bool, message: str = ""):
    """Record test result."""
    if passed:
        print(f"  ✓ {test_name}")
        test_results["passed"] += 1
    else:
        print(f"  ✗ {test_name}")
        if message:
            print(f"    Error: {message}")
        test_results["failed"] += 1
        test_results["errors"].append(f"{test_name}: {message}")

def make_request(endpoint: str, method: str = "GET", api_key: Optional[str] = None, 
                 super_user_key: Optional[str] = None, data: Optional[Dict] = None):
    """Make HTTP request with optional authentication."""
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if api_key:
        headers['X-API-Key'] = api_key
    if super_user_key:
        headers['X-Super-User-Key'] = super_user_key
    
    try:
        if method == "GET":
            return requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            return requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
        elif method == "DELETE":
            return requests.delete(url, headers=headers, timeout=TIMEOUT)
    except Exception as e:
        return None

# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

def test_authentication():
    """Test API authentication and authorization."""
    print("\n" + "="*70)
    print("AUTHENTICATION TESTS")
    print("="*70)
    
    # Test 1: Public endpoints (no auth required)
    print("\n1. Public Endpoints (No Authentication)")
    
    response = make_request("/")
    test_result(
        "GET / - Home endpoint accessible",
        response is not None and response.status_code == 200
    )
    
    response = make_request("/health")
    test_result(
        "GET /health - Health check accessible",
        response is not None and response.status_code == 200
    )
    
    response = make_request("/version")
    test_result(
        "GET /version - Version info accessible",
        response is not None and response.status_code == 200
    )
    
    # Test 2: Protected endpoint without auth
    print("\n2. Protected Endpoints (Missing Authentication)")
    
    response = make_request("/convert", method="POST", data={"html": "<h1>Test</h1>"})
    test_result(
        "POST /convert without API key - Should return 401",
        response is not None and response.status_code == 401,
        f"Expected 401, got {response.status_code if response else 'None'}"
    )
    
    # Test 3: Invalid API key
    print("\n3. Invalid API Key")
    
    response = make_request("/convert", method="POST", api_key=INVALID_API_KEY, 
                           data={"html": "<h1>Test</h1>"})
    test_result(
        "POST /convert with invalid API key - Should return 403",
        response is not None and response.status_code == 403,
        f"Expected 403, got {response.status_code if response else 'None'}"
    )
    
    # Test 4: Inactive API key
    print("\n4. Inactive API Key")
    
    response = make_request("/convert", method="POST", api_key=INACTIVE_API_KEY,
                           data={"html": "<h1>Test</h1>"})
    test_result(
        "POST /convert with inactive API key - Should return 403",
        response is not None and response.status_code == 403,
        f"Expected 403, got {response.status_code if response else 'None'}"
    )
    
    # Test 5: Valid API key
    print("\n5. Valid API Key")
    
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": "<h1>Test</h1>", "filename": "test.pdf"})
    test_result(
        "POST /convert with valid API key - Should return 200",
        response is not None and response.status_code == 200,
        f"Expected 200, got {response.status_code if response else 'None'}"
    )
    
    # Test 6: Super user endpoints
    print("\n6. Super User Endpoints")
    
    response = make_request("/admin/keys", method="GET")
    test_result(
        "GET /admin/keys without super user key - Should return 401",
        response is not None and response.status_code == 401,
        f"Expected 401, got {response.status_code if response else 'None'}"
    )
    
    response = make_request("/admin/keys", method="GET", super_user_key="wrong-key")
    test_result(
        "GET /admin/keys with invalid super user key - Should return 403",
        response is not None and response.status_code == 403,
        f"Expected 403, got {response.status_code if response else 'None'}"
    )
    
    response = make_request("/admin/keys", method="GET", super_user_key=SUPER_USER_KEY)
    test_result(
        "GET /admin/keys with valid super user key - Should return 200",
        response is not None and response.status_code == 200,
        f"Expected 200, got {response.status_code if response else 'None'}"
    )

# =============================================================================
# RATE LIMITING TESTS
# =============================================================================

def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\n" + "="*70)
    print("RATE LIMITING TESTS")
    print("="*70)
    
    print("\n1. Per-Minute Rate Limit (5 requests/minute)")
    
    # Make 5 requests quickly (should succeed)
    successes = 0
    for i in range(5):
        response = make_request("/convert", method="POST", api_key=RATELIMIT_API_KEY,
                               data={"html": f"<h1>Request {i+1}</h1>"})
        if response and response.status_code == 200:
            successes += 1
    
    test_result(
        "First 5 requests within rate limit - Should succeed",
        successes == 5,
        f"Expected 5 successes, got {successes}"
    )
    
    # 6th request should be rate limited
    response = make_request("/convert", method="POST", api_key=RATELIMIT_API_KEY,
                           data={"html": "<h1>Request 6</h1>"})
    test_result(
        "6th request exceeds per-minute limit - Should return 429",
        response is not None and response.status_code == 429,
        f"Expected 429, got {response.status_code if response else 'None'}"
    )
    
    print("\n  Waiting 10 seconds for rate limit window...")
    time.sleep(10)
    
    # After waiting, should work again
    response = make_request("/convert", method="POST", api_key=RATELIMIT_API_KEY,
                           data={"html": "<h1>After wait</h1>"})
    test_result(
        "Request after partial wait - Should succeed",
        response is not None and response.status_code == 200,
        f"Expected 200, got {response.status_code if response else 'None'}"
    )

# =============================================================================
# HTML CONVERSION TESTS
# =============================================================================

def test_html_conversion():
    """Test various HTML conversion scenarios."""
    print("\n" + "="*70)
    print("HTML CONVERSION TESTS")
    print("="*70)
    
    print("\n1. Simple Valid HTML")
    
    html = "<html><body><h1>Hello World</h1></body></html>"
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": html, "filename": "simple.pdf"})
    test_result(
        "Convert simple HTML - Should return PDF",
        response is not None and response.status_code == 200 and 
        response.headers.get('Content-Type') == 'application/pdf',
        f"Status: {response.status_code if response else 'None'}, " +
        f"Type: {response.headers.get('Content-Type') if response else 'None'}"
    )
    
    print("\n2. HTML with CSS Styles")
    
    html = """
    <html>
        <head>
            <style>
                body { font-family: Arial; background: #f0f0f0; padding: 20px; }
                h1 { color: #333; }
            </style>
        </head>
        <body><h1>Styled Content</h1><p>This has CSS.</p></body>
    </html>
    """
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": html, "filename": "styled.pdf"})
    test_result(
        "Convert HTML with inline CSS",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )
    
    print("\n3. HTML with Separate CSS")
    
    html = "<html><body><h1 class='title'>Title</h1></body></html>"
    css = ".title { color: blue; font-size: 24px; }"
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": html, "css": css, "filename": "separate-css.pdf"})
    test_result(
        "Convert HTML with separate CSS parameter",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )
    
    print("\n4. Broken/Malformed HTML")
    
    html = "<div style=maxheight:100px><p>Unclosed tags<div>More content"
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": html, "filename": "broken.pdf"})
    test_result(
        "Convert broken HTML - Should handle gracefully",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )
    
    print("\n5. Large HTML Document")
    
    # Generate large HTML
    html = "<html><body>"
    for i in range(1000):
        html += f"<p>Paragraph {i+1} with some content</p>"
    html += "</body></html>"
    
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": html, "filename": "large.pdf"})
    test_result(
        "Convert large HTML document (1000 paragraphs)",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )
    
    if response and response.status_code == 200:
        print(f"    Generated PDF size: {len(response.content):,} bytes")
    
    print("\n6. Different Page Sizes")
    
    for page_size in ['A4', 'Letter', 'Legal', 'A3']:
        html = f"<html><body><h1>Page Size: {page_size}</h1></body></html>"
        response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                               data={"html": html, "page_size": page_size})
        test_result(
            f"Convert with page size: {page_size}",
            response is not None and response.status_code == 200,
            f"Status: {response.status_code if response else 'None'}"
        )
    
    print("\n7. Custom Margins")
    
    html = "<html><body><h1>Custom Margins</h1></body></html>"
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": html, "margin": "20px"})
    test_result(
        "Convert with custom margins (20px)",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )
    
    print("\n8. Custom Viewport")
    
    html = "<html><body><h1>Custom Viewport</h1></body></html>"
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={
                               "html": html,
                               "viewport_width": 1024,
                               "viewport_height": 768
                           })
    test_result(
        "Convert with custom viewport (1024x768)",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )

# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

def test_error_handling():
    """Test error handling scenarios."""
    print("\n" + "="*70)
    print("ERROR HANDLING TESTS")
    print("="*70)
    
    print("\n1. Missing Required Fields")
    
    # Missing HTML content
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"filename": "test.pdf"})
    test_result(
        "Request without HTML content - Should return 400",
        response is not None and response.status_code == 400,
        f"Expected 400, got {response.status_code if response else 'None'}"
    )
    
    # Empty HTML
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": ""})
    test_result(
        "Request with empty HTML - Should return 400",
        response is not None and response.status_code == 400,
        f"Expected 400, got {response.status_code if response else 'None'}"
    )
    
    # No JSON body
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data=None)
    test_result(
        "Request without JSON body - Should return 400",
        response is not None and response.status_code == 400,
        f"Expected 400, got {response.status_code if response else 'None'}"
    )
    
    print("\n2. Invalid Endpoints")
    
    response = make_request("/nonexistent", method="GET")
    test_result(
        "Request to non-existent endpoint - Should return 404",
        response is not None and response.status_code == 404,
        f"Expected 404, got {response.status_code if response else 'None'}"
    )
    
    print("\n3. Special Characters in HTML")
    
    html = "<html><body><h1>Special: & < > \" ' © ®</h1></body></html>"
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": html})
    test_result(
        "HTML with special characters - Should handle correctly",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )
    
    print("\n4. Unicode Characters")
    
    html = "<html><body><h1>Unicode: 你好 مرحبا Привет 🎉 ❤️</h1></body></html>"
    response = make_request("/convert", method="POST", api_key=VALID_API_KEY,
                           data={"html": html})
    test_result(
        "HTML with unicode characters - Should handle correctly",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )

# =============================================================================
# ADMIN ENDPOINT TESTS
# =============================================================================

def test_admin_endpoints():
    """Test admin endpoints."""
    print("\n" + "="*70)
    print("ADMIN ENDPOINT TESTS")
    print("="*70)
    
    print("\n1. List API Keys")
    
    response = make_request("/admin/keys", method="GET", super_user_key=SUPER_USER_KEY)
    test_result(
        "GET /admin/keys - Should return key list",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )
    
    if response and response.status_code == 200:
        data = response.json()
        print(f"    Found {len(data.get('api_keys', []))} API keys")
    
    print("\n2. Rate Limit Info")
    
    response = make_request("/admin/rate-limit", method="GET", super_user_key=SUPER_USER_KEY)
    test_result(
        "GET /admin/rate-limit - Should return rate limit config",
        response is not None and response.status_code == 200,
        f"Status: {response.status_code if response else 'None'}"
    )

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*70)
    print("HTML-to-PDF API - PRODUCTION TEST SUITE")
    print("="*70)
    print(f"\nTesting against: {BASE_URL}")
    print(f"Timeout: {TIMEOUT}s")
    print("\nNOTE: Make sure the server is running with test configuration:")
    print("  1. Copy .api-keys.test.json to .api-keys.json")
    print("  2. Start server: python app.py")
    
    # Check if server is running
    print("\nChecking server availability...")
    response = make_request("/health")
    if not response or response.status_code != 200:
        print("\n❌ ERROR: Server is not responding!")
        print("   Please start the server first: python app.py")
        sys.exit(1)
    print("✓ Server is running")
    
    # Run test suites
    test_authentication()
    test_rate_limiting()
    test_html_conversion()
    test_error_handling()
    test_admin_endpoints()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\n✓ Passed: {test_results['passed']}")
    print(f"✗ Failed: {test_results['failed']}")
    print(f"Total:   {test_results['passed'] + test_results['failed']}")
    
    if test_results['failed'] > 0:
        print("\n❌ FAILED TESTS:")
        for error in test_results['errors']:
            print(f"  - {error}")
        print("\n⚠️  Some tests failed - please review before deploying!")
        sys.exit(1)
    else:
        print("\n✅ ALL TESTS PASSED!")
        print("🚀 API is ready for production deployment!")
        sys.exit(0)

if __name__ == '__main__':
    run_all_tests()
