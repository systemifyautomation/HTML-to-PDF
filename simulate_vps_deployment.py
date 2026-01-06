"""
VPS Deployment Simulation Script
Sets up and tests the API in a production-like environment on Windows
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

class DeploymentSimulator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = []
        
    def print_step(self, step_num, description):
        """Print step header."""
        print(f"\n{'='*70}")
        print(f"STEP {step_num}: {description}")
        print(f"{'='*70}\n")
    
    def print_success(self, message):
        """Print success message."""
        print(f"✓ {message}")
        self.test_results.append(("✓", message))
    
    def print_error(self, message):
        """Print error message."""
        print(f"✗ {message}")
        self.test_results.append(("✗", message))
    
    def print_info(self, message):
        """Print info message."""
        print(f"  {message}")
    
    def run_command(self, command, description, check=True):
        """Run a shell command."""
        self.print_info(f"Running: {description}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        self.print_info(f"  {line}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.print_error(f"Command failed: {e}")
            if e.stderr:
                self.print_info(f"  Error: {e.stderr}")
            return False, e.stderr
    
    def setup_test_environment(self):
        """Step 1: Set up test environment."""
        self.print_step(1, "Setting Up Test Environment")
        
        # Copy test API keys to production location
        test_keys = self.project_root / '.api-keys.test.json'
        prod_keys = self.project_root / '.api-keys.json'
        
        if test_keys.exists():
            shutil.copy(test_keys, prod_keys)
            self.print_success("Copied test API keys to .api-keys.json")
        else:
            self.print_error(".api-keys.test.json not found")
            return False
        
        # Check if playwright is installed
        success, output = self.run_command(
            'python -c "import playwright; print(playwright.__version__)"',
            "Checking Playwright installation",
            check=False
        )
        
        if success:
            self.print_success("Playwright is installed")
        else:
            self.print_error("Playwright not installed")
            return False
        
        # Check if Chromium is installed
        success, output = self.run_command(
            'playwright show',
            "Checking Playwright browsers",
            check=False
        )
        
        if success:
            self.print_success("Playwright browsers are installed")
        else:
            self.print_info("Installing Chromium browser...")
            success, _ = self.run_command(
                'playwright install chromium',
                "Installing Chromium"
            )
            if success:
                self.print_success("Chromium installed")
            else:
                self.print_error("Failed to install Chromium")
                return False
        
        return True
    
    def check_dependencies(self):
        """Step 2: Check all dependencies."""
        self.print_step(2, "Checking Dependencies")
        
        dependencies = {
            'Flask': 'flask',
            'Playwright': 'playwright',
            'Requests': 'requests',
            'Python-dotenv': 'dotenv'
        }
        
        all_ok = True
        for name, module in dependencies.items():
            success, _ = self.run_command(
                f'python -c "import {module}"',
                f"Checking {name}",
                check=False
            )
            if success:
                self.print_success(f"{name} is installed")
            else:
                self.print_error(f"{name} is NOT installed")
                all_ok = False
        
        return all_ok
    
    def test_api_startup(self):
        """Step 3: Test API startup."""
        self.print_step(3, "Testing API Startup")
        
        self.print_info("Starting Flask server in background...")
        
        # Start server in background
        try:
            process = subprocess.Popen(
                ['python', 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            # Wait for server to start
            self.print_info("Waiting for server to start...")
            time.sleep(5)
            
            # Check if server is running
            import requests
            try:
                response = requests.get('http://localhost:5000/health', timeout=10)
                if response.status_code == 200:
                    self.print_success("Server started successfully")
                    server_running = True
                else:
                    self.print_error(f"Server returned status {response.status_code}")
                    server_running = False
            except Exception as e:
                self.print_error(f"Could not connect to server: {e}")
                server_running = False
            
            # Keep server running for tests
            if server_running:
                return True, process
            else:
                process.terminate()
                return False, None
                
        except Exception as e:
            self.print_error(f"Failed to start server: {e}")
            return False, None
    
    def run_test_suite(self, test_file, description):
        """Run a test suite."""
        self.print_info(f"Running {description}...")
        success, output = self.run_command(
            f'python {test_file}',
            description,
            check=False
        )
        return success
    
    def run_all_tests(self):
        """Step 4: Run all test suites."""
        self.print_step(4, "Running Test Suites")
        
        test_files = [
            ('test_simple_api.py', 'Simple API Test'),
            ('test_vps_simulation.py', 'VPS Simulation Test'),
        ]
        
        all_passed = True
        for test_file, description in test_files:
            if (self.project_root / test_file).exists():
                success = self.run_test_suite(test_file, description)
                if success:
                    self.print_success(f"{description} passed")
                else:
                    self.print_error(f"{description} failed")
                    all_passed = False
            else:
                self.print_info(f"Skipping {description} (file not found)")
        
        return all_passed
    
    def cleanup(self, process):
        """Step 5: Cleanup."""
        self.print_step(5, "Cleanup")
        
        if process:
            self.print_info("Stopping Flask server...")
            process.terminate()
            try:
                process.wait(timeout=5)
                self.print_success("Server stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                self.print_info("Server forcefully killed")
        
        # Optionally remove test API keys
        self.print_info("Test API keys remain in .api-keys.json for manual testing")
        self.print_info("Remove them before production deployment!")
    
    def print_summary(self):
        """Print final summary."""
        print(f"\n{'='*70}")
        print("DEPLOYMENT SIMULATION SUMMARY")
        print(f"{'='*70}\n")
        
        passed = sum(1 for status, _ in self.test_results if status == "✓")
        failed = sum(1 for status, _ in self.test_results if status == "✗")
        
        print(f"Total checks: {len(self.test_results)}")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}\n")
        
        if failed == 0:
            print("✅ ALL CHECKS PASSED!")
            print("\n🚀 Your API is ready for VPS deployment!")
            print("\nNext steps:")
            print("  1. Generate production API keys: python generate_api_key.py")
            print("  2. Update .api-keys.json with production keys")
            print("  3. Deploy to VPS following DEPLOYMENT.md")
            print("  4. Test production endpoint with test_production.py")
        else:
            print("❌ SOME CHECKS FAILED")
            print("\n⚠️  Please fix the issues before deploying to VPS")
            print("\nFailed checks:")
            for status, message in self.test_results:
                if status == "✗":
                    print(f"  - {message}")
    
    def run(self):
        """Run full deployment simulation."""
        print("\n" + "="*70)
        print("VPS DEPLOYMENT SIMULATION")
        print("="*70)
        print("\nThis script simulates a production VPS deployment on your local machine.")
        print("It will:")
        print("  1. Set up test environment with API keys")
        print("  2. Check all dependencies")
        print("  3. Start the Flask server")
        print("  4. Run comprehensive test suites")
        print("  5. Generate deployment readiness report")
        
        input("\nPress Enter to continue...")
        
        # Step 1: Setup
        if not self.setup_test_environment():
            self.print_summary()
            return False
        
        # Step 2: Check dependencies
        if not self.check_dependencies():
            self.print_summary()
            return False
        
        # Step 3: Start server
        server_ok, process = self.test_api_startup()
        if not server_ok:
            self.print_summary()
            return False
        
        try:
            # Step 4: Run tests
            self.run_all_tests()
            
        finally:
            # Step 5: Cleanup
            self.cleanup(process)
        
        # Print summary
        self.print_summary()
        
        return all(status == "✓" for status, _ in self.test_results)

if __name__ == '__main__':
    simulator = DeploymentSimulator()
    success = simulator.run()
    sys.exit(0 if success else 1)
