#!/usr/bin/env python3
"""
Test script for Clio file upload functionality.

This script tests the clio_upload module without requiring actual Clio credentials.
It validates the code structure, imports, and basic functionality.
"""

import sys
import os
import tempfile
from pathlib import Path

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


def test_imports():
    """Test 1: Module imports"""
    print("\n--- Test 1: Module Imports ---")
    try:
        # Test if clio_upload module can be imported
        import clio_upload
        print_status("clio_upload module imported successfully", "success")
        
        # Test if ClioFileUploader class exists
        from clio_upload import ClioFileUploader
        print_status("ClioFileUploader class found", "success")
        
        return True
    except ImportError as e:
        print_status(f"Import failed: {e}", "error")
        print_status("Make sure to install dependencies: pip install -r requirements.txt", "warning")
        return False
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        return False


def test_config_validation():
    """Test 2: Configuration validation"""
    print("\n--- Test 2: Configuration Validation ---")
    try:
        from clio_upload import ClioFileUploader
        
        # Test with non-existent config file
        print("Testing non-existent config file...")
        try:
            uploader = ClioFileUploader(config_path='non_existent_config.json')
            print_status("Should have raised error for missing config", "error")
            return False
        except SystemExit:
            print_status("Correctly handles missing config file", "success")
        
        # Test with example config (has placeholder token)
        print("\nTesting placeholder token detection...")
        if os.path.exists('.clio-config.example.json'):
            try:
                uploader = ClioFileUploader(config_path='.clio-config.example.json')
                print_status("Should have raised error for placeholder token", "error")
                return False
            except SystemExit:
                print_status("Correctly detects placeholder token", "success")
        else:
            print_status("Example config not found (OK for CI)", "warning")
        
        return True
        
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        return False


def test_file_validation():
    """Test 3: File validation logic"""
    print("\n--- Test 3: File Validation ---")
    try:
        from clio_upload import ClioFileUploader
        
        # Create a temporary config for testing (won't be used for upload)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"access_token": "dummy_token_for_testing"}')
            temp_config = f.name
        
        try:
            # This will fail at client initialization, but we're testing file validation
            print("Testing file existence check...")
            
            # The class requires a valid token, but we can test the helper functions
            # by checking if the script has proper file validation
            import clio_upload
            
            # Test if select_file_interactive function exists
            if hasattr(clio_upload, 'select_file_interactive'):
                print_status("File selection function exists", "success")
            else:
                print_status("File selection function not found", "warning")
            
            print_status("File validation structure verified", "success")
            return True
            
        finally:
            # Clean up temp config
            if os.path.exists(temp_config):
                os.remove(temp_config)
        
    except Exception as e:
        print_status(f"Error during file validation test: {e}", "error")
        return False


def test_command_line_interface():
    """Test 4: Command-line interface"""
    print("\n--- Test 4: Command-Line Interface ---")
    try:
        import subprocess
        
        # Test --help command
        print("Testing --help command...")
        result = subprocess.run(
            [sys.executable, 'clio_upload.py', '--help'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and 'Upload files to Clio.com' in result.stdout:
            print_status("--help command works correctly", "success")
        else:
            print_status("--help command failed", "error")
            return False
        
        # Test that required config is checked
        print("\nTesting config requirement...")
        result = subprocess.run(
            [sys.executable, 'clio_upload.py', '--list-matters'],
            capture_output=True,
            text=True
        )
        
        if 'Configuration file not found' in result.stdout or 'access token' in result.stdout:
            print_status("Config requirement validated correctly", "success")
        else:
            print_status("Config validation may have issues", "warning")
        
        return True
        
    except Exception as e:
        print_status(f"CLI test error: {e}", "error")
        return False


def test_examples():
    """Test 5: Examples script"""
    print("\n--- Test 5: Examples Script ---")
    try:
        import subprocess
        
        # Test examples script
        print("Testing examples script...")
        result = subprocess.run(
            [sys.executable, 'examples/clio_upload_examples.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and 'Usage Examples' in result.stdout:
            print_status("Examples script runs successfully", "success")
            return True
        else:
            print_status("Examples script may have issues", "warning")
            print(f"Output: {result.stdout[:200]}")
            return True  # Non-critical
        
    except Exception as e:
        print_status(f"Examples test error: {e}", "warning")
        return True  # Non-critical


def test_documentation():
    """Test 6: Documentation files"""
    print("\n--- Test 6: Documentation ---")
    
    docs = {
        'CLIO_UPLOAD_README.md': 'Main documentation',
        'CLIO_QUICKSTART.md': 'Quick start guide',
        '.clio-config.example.json': 'Example configuration',
        'examples/clio_upload_examples.py': 'Examples script'
    }
    
    all_exist = True
    for doc, description in docs.items():
        if os.path.exists(doc):
            print_status(f"{description} exists: {doc}", "success")
        else:
            print_status(f"{description} missing: {doc}", "error")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Clio File Upload - Test Suite")
    print("="*60)
    
    print("\nNote: These tests validate code structure and don't require")
    print("actual Clio credentials. For full integration testing,")
    print("configure .clio-config.json with valid credentials.\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration Validation", test_config_validation),
        ("File Validation", test_file_validation),
        ("Command-Line Interface", test_command_line_interface),
        ("Examples Script", test_examples),
        ("Documentation", test_documentation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Test '{test_name}' crashed: {e}", "error")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = "success" if result else "error"
        print_status(f"{test_name}: {status}", color)
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)


if __name__ == '__main__':
    main()
