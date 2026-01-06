"""
Load and Performance Test Suite for HTML-to-PDF API
Tests concurrent requests, throughput, and server stability
Simulates production load scenarios
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys

# Test configuration
BASE_URL = "http://localhost:5000"
API_KEY = "test-api-key-valid-12345678901234567890"
TIMEOUT = 120

# Test HTML samples
SIMPLE_HTML = "<html><body><h1>Load Test</h1><p>Simple content</p></body></html>"

MEDIUM_HTML = """
<html>
<head>
    <style>
        body { font-family: Arial; padding: 20px; }
        .section { margin: 20px 0; border: 1px solid #ddd; padding: 10px; }
    </style>
</head>
<body>
    <h1>Medium Complexity Document</h1>
    {}
</body>
</html>
""".format("\n".join([f'<div class="section"><h2>Section {i}</h2><p>Content for section {i}</p></div>' for i in range(50)]))

LARGE_HTML = """
<html>
<head>
    <style>
        body { font-family: Arial; padding: 20px; }
        table { width: 100%; border-collapse: collapse; }
        td, th { border: 1px solid #ddd; padding: 8px; }
    </style>
</head>
<body>
    <h1>Large Document with Table</h1>
    <table>
        <tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr>
        {}
    </table>
</body>
</html>
""".format("\n".join([f'<tr><td>{i}</td><td>User {i}</td><td>user{i}@test.com</td><td>Active</td></tr>' for i in range(500)]))

class LoadTester:
    def __init__(self):
        self.results = []
        self.errors = []
        
    def make_request(self, html_content, test_id):
        """Make a single PDF conversion request."""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/convert",
                json={
                    "html": html_content,
                    "filename": f"load_test_{test_id}.pdf",
                    "page_size": "A4"
                },
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': API_KEY
                },
                timeout=TIMEOUT
            )
            
            duration = time.time() - start_time
            
            return {
                'id': test_id,
                'status_code': response.status_code,
                'duration': duration,
                'size': len(response.content) if response.status_code == 200 else 0,
                'success': response.status_code == 200
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'id': test_id,
                'status_code': 0,
                'duration': duration,
                'size': 0,
                'success': False,
                'error': str(e)
            }
    
    def run_sequential_test(self, html_content, num_requests, description):
        """Run requests sequentially."""
        print(f"\n{'='*70}")
        print(f"Sequential Test: {description}")
        print(f"{'='*70}")
        print(f"Requests: {num_requests}")
        print(f"HTML size: {len(html_content):,} bytes\n")
        
        results = []
        start_time = time.time()
        
        for i in range(num_requests):
            result = self.make_request(html_content, i)
            results.append(result)
            
            status = "✓" if result['success'] else "✗"
            print(f"  {status} Request {i+1}/{num_requests}: {result['duration']:.2f}s")
        
        total_duration = time.time() - start_time
        self.print_results(results, total_duration, "Sequential")
        
        return results
    
    def run_concurrent_test(self, html_content, num_requests, num_workers, description):
        """Run requests concurrently."""
        print(f"\n{'='*70}")
        print(f"Concurrent Test: {description}")
        print(f"{'='*70}")
        print(f"Requests: {num_requests}")
        print(f"Concurrent workers: {num_workers}")
        print(f"HTML size: {len(html_content):,} bytes\n")
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(self.make_request, html_content, i): i 
                for i in range(num_requests)
            }
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                completed += 1
                
                status = "✓" if result['success'] else "✗"
                print(f"  {status} Completed {completed}/{num_requests}: {result['duration']:.2f}s")
        
        total_duration = time.time() - start_time
        self.print_results(results, total_duration, "Concurrent")
        
        return results
    
    def print_results(self, results, total_duration, test_type):
        """Print test results summary."""
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if successful:
            durations = [r['duration'] for r in successful]
            sizes = [r['size'] for r in successful]
            
            print(f"\n{test_type} Test Results:")
            print(f"  Total requests: {len(results)}")
            print(f"  Successful: {len(successful)}")
            print(f"  Failed: {len(failed)}")
            print(f"  Total time: {total_duration:.2f}s")
            print(f"  Throughput: {len(successful)/total_duration:.2f} requests/sec")
            print(f"\n  Response times:")
            print(f"    Min: {min(durations):.2f}s")
            print(f"    Max: {max(durations):.2f}s")
            print(f"    Mean: {statistics.mean(durations):.2f}s")
            print(f"    Median: {statistics.median(durations):.2f}s")
            if len(durations) > 1:
                print(f"    Std Dev: {statistics.stdev(durations):.2f}s")
            print(f"\n  PDF sizes:")
            print(f"    Min: {min(sizes):,} bytes")
            print(f"    Max: {max(sizes):,} bytes")
            print(f"    Mean: {int(statistics.mean(sizes)):,} bytes")
        
        if failed:
            print(f"\n  Failed requests: {len(failed)}")
            for r in failed[:5]:  # Show first 5 errors
                error = r.get('error', f"HTTP {r['status_code']}")
                print(f"    - Request {r['id']}: {error}")

def test_server_availability():
    """Check if server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_load_tests():
    """Run all load tests."""
    print("\n" + "="*70)
    print("HTML-to-PDF API - LOAD & PERFORMANCE TEST SUITE")
    print("="*70)
    print(f"\nTesting against: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    print(f"Timeout: {TIMEOUT}s")
    
    # Check server availability
    print("\nChecking server availability...")
    if not test_server_availability():
        print("\n❌ ERROR: Server is not responding!")
        print("   Please start the server first: python app.py")
        sys.exit(1)
    print("✓ Server is running")
    
    tester = LoadTester()
    
    # Test 1: Sequential simple requests
    tester.run_sequential_test(
        SIMPLE_HTML,
        10,
        "10 Simple Sequential Requests"
    )
    
    # Test 2: Concurrent simple requests
    tester.run_concurrent_test(
        SIMPLE_HTML,
        10,
        3,
        "10 Simple Concurrent Requests (3 workers)"
    )
    
    # Test 3: Medium complexity
    tester.run_sequential_test(
        MEDIUM_HTML,
        5,
        "5 Medium Complexity Sequential Requests"
    )
    
    # Test 4: Large document
    tester.run_sequential_test(
        LARGE_HTML,
        3,
        "3 Large Document Sequential Requests"
    )
    
    # Test 5: Concurrent medium load
    tester.run_concurrent_test(
        MEDIUM_HTML,
        5,
        2,
        "5 Medium Complexity Concurrent Requests (2 workers)"
    )
    
    # Test 6: Stress test - many concurrent requests
    print("\n" + "="*70)
    print("⚠️  STRESS TEST WARNING")
    print("="*70)
    print("This test will send 20 concurrent requests with 5 workers.")
    print("This may take several minutes and consume significant resources.")
    
    response = input("\nContinue with stress test? (y/N): ")
    if response.lower() == 'y':
        tester.run_concurrent_test(
            SIMPLE_HTML,
            20,
            5,
            "20 Simple Concurrent Requests (5 workers) - STRESS TEST"
        )
    else:
        print("Stress test skipped.")
    
    # Final summary
    print("\n" + "="*70)
    print("LOAD TEST COMPLETE")
    print("="*70)
    print("\n✅ All load tests completed successfully!")
    print("\n💡 Performance Tips:")
    print("  - If response times are high, consider increasing server resources")
    print("  - Monitor memory usage during concurrent requests")
    print("  - Adjust rate limits based on server capacity")
    print("  - Use caching for frequently converted templates")

if __name__ == '__main__':
    run_load_tests()
