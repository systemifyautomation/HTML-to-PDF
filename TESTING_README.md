# 🧪 Production Testing Suite - Quick Reference

## 🎯 Quick Start (30 seconds)

```powershell
# Option 1: PowerShell quick test
.\quick-test.ps1

# Option 2: Python automated test
python simulate_vps_deployment.py
```

---

## 📁 Test Files

| File | Purpose | Run Time | When to Use |
|------|---------|----------|-------------|
| `quick-test.ps1` | Quick sanity check | ~10s | First test, quick validation |
| `test_simple_api.py` | Basic API test | ~5s | Quick functionality check |
| `test_vps_simulation.py` | Full test suite | ~2min | Before deployment |
| `test_load_performance.py` | Performance tests | ~5min | Check server capacity |
| `simulate_vps_deployment.py` | Complete simulation | ~3min | Final pre-deployment check |

---

## 🚀 Testing Workflow

### 1️⃣ Quick Check (Before You Start)

```powershell
.\quick-test.ps1
```

**Checks:**
- ✓ Dependencies installed
- ✓ API keys configured
- ✓ Server starts
- ✓ Basic conversion works

**Time:** 10 seconds

---

### 2️⃣ Full Test Suite (Before Deployment)

**Start server:**
```powershell
# Copy test API keys
Copy-Item .api-keys.test.json .api-keys.json

# Start server
python app.py
```

**In new terminal, run tests:**
```powershell
python test_vps_simulation.py
```

**What it tests:**
- ✓ Authentication (8 tests)
- ✓ Rate limiting (4 tests)
- ✓ HTML conversion (8 tests)
- ✓ Error handling (4 tests)
- ✓ Admin endpoints (2 tests)

**Expected:** `✅ ALL TESTS PASSED! 🚀 API is ready for production deployment!`

**Time:** 2-3 minutes

---

### 3️⃣ Performance Testing (Optional but Recommended)

```powershell
python test_load_performance.py
```

**What it tests:**
- Sequential requests (simple, medium, large HTML)
- Concurrent requests (2-5 workers)
- Response times and throughput
- Server stability under load
- Optional stress test (20 concurrent requests)

**Time:** 5-10 minutes

---

### 4️⃣ Full Deployment Simulation (Comprehensive)

```powershell
python simulate_vps_deployment.py
```

**What it does:**
1. Sets up test environment
2. Checks all dependencies
3. Starts server automatically
4. Runs all test suites
5. Generates deployment report

**Expected:** `✅ ALL CHECKS PASSED! 🚀 Your API is ready for VPS deployment!`

**Time:** 3-5 minutes

---

## 📊 Test Results Interpretation

### ✅ Success

```
✓ Passed: 35
✗ Failed: 0
✅ ALL TESTS PASSED!
```

**Action:** You're ready to deploy! 🚀

---

### ⚠️ Partial Failures

```
✓ Passed: 30
✗ Failed: 5
```

**Common Issues:**

**Rate limiting tests fail:**
- Wait 60s between test runs
- Restart server to clear rate limit cache

**Timeout errors:**
- Increase timeout in test files
- Check if server has enough resources

**Connection errors:**
- Ensure server is running
- Check port 5000 is available

---

### ❌ Total Failure

```
❌ ERROR: Server is not responding!
```

**Troubleshooting:**

1. **Check server is running:**
   ```powershell
   # Visit in browser
   http://localhost:5000/health
   ```

2. **Check for errors:**
   ```powershell
   # Look at server console for errors
   ```

3. **Reinstall dependencies:**
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Kill conflicting processes:**
   ```powershell
   taskkill /F /IM python.exe
   Start-Sleep -Seconds 2
   python app.py
   ```

---

## 🔑 Test API Keys

From `.api-keys.test.json`:

```
Valid API Key:      test-api-key-valid-12345678901234567890
Inactive API Key:   test-api-key-inactive-12345678901234567890
Rate Limit Key:     test-api-key-ratelimit-12345678901234567890
Super User Key:     test-super-user-key-12345678901234567890
```

**Rate Limits:** 5 requests/minute, 20 requests/hour (for quick testing)

---

## 📈 Performance Benchmarks

**Expected Performance (local testing):**

| HTML Type | Size | Response Time | PDF Size |
|-----------|------|---------------|----------|
| Simple | <1KB | 1-2s | ~30KB |
| Medium | 5-10KB | 2-4s | ~100KB |
| Large | 50KB+ | 4-8s | ~300KB |

**Throughput:**
- Sequential: 2-5 requests/sec
- Concurrent (3 workers): 1-3 requests/sec

**Note:** VPS performance may vary based on resources.

---

## 🎬 Example Test Run

```powershell
PS> python test_vps_simulation.py

======================================================================
HTML-to-PDF API - PRODUCTION TEST SUITE
======================================================================

Testing against: http://localhost:5000
Timeout: 60s

Checking server availability...
✓ Server is running

======================================================================
AUTHENTICATION TESTS
======================================================================

1. Public Endpoints (No Authentication)
  ✓ GET / - Home endpoint accessible
  ✓ GET /health - Health check accessible
  ✓ GET /version - Version info accessible

2. Protected Endpoints (Missing Authentication)
  ✓ POST /convert without API key - Should return 401

3. Invalid API Key
  ✓ POST /convert with invalid API key - Should return 403

... (continues with all tests)

======================================================================
TEST SUMMARY
======================================================================

✓ Passed: 35
✗ Failed: 0
Total:   35

✅ ALL TESTS PASSED!
🚀 API is ready for production deployment!
```

---

## 🛠️ Troubleshooting

### Server Won't Start

```powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Wait and restart
Start-Sleep -Seconds 2
python app.py
```

### Tests Timeout

Increase timeout in test files:
```python
TIMEOUT = 120  # Increase to 120 seconds
```

### Playwright Errors

```powershell
# Reinstall browsers
playwright install chromium
```

### Port Conflicts

```powershell
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /F /PID <PID>
```

---

## 📋 Pre-Deployment Checklist

- [ ] Quick test passes (`.\quick-test.ps1`)
- [ ] Full test suite passes (`test_vps_simulation.py`)
- [ ] Load tests show acceptable performance
- [ ] All dependencies installed
- [ ] Production API keys generated
- [ ] `.api-keys.json` updated for production
- [ ] Rate limits set appropriately
- [ ] Security checklist completed

**When all checked:** Deploy to VPS following `DEPLOYMENT.md`

---

## 🎯 One-Liner Commands

```powershell
# Quick test everything
.\quick-test.ps1

# Full automated test
python simulate_vps_deployment.py

# Just run API tests (server must be running)
python test_vps_simulation.py

# Performance test
python test_load_performance.py

# Simple sanity check
python test_simple_api.py
```

---

## 📞 Need Help?

1. Check [VPS_TESTING_GUIDE.md](VPS_TESTING_GUIDE.md) for detailed documentation
2. Review [CHROME_ERROR_FIXED.md](CHROME_ERROR_FIXED.md) for Playwright setup
3. See [DEPLOYMENT.md](DEPLOYMENT.md) for VPS deployment

---

**Ready to test? Run:**

```powershell
.\quick-test.ps1
```

**Good luck! 🚀**
