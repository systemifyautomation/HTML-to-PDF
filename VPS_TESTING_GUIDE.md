# VPS Deployment Testing Guide

Complete guide for testing your HTML-to-PDF API before deploying to production VPS.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Files Overview](#test-files-overview)
3. [Running Tests](#running-tests)
4. [Test Coverage](#test-coverage)
5. [Before Deployment Checklist](#before-deployment-checklist)

---

## 🚀 Quick Start

### Prerequisites

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Set up test environment:**
   ```powershell
   # Copy test API keys
   Copy-Item .api-keys.test.json .api-keys.json
   
   # Start the server
   python app.py
   ```

### Run All Tests (Automated)

The easiest way to test everything:

```powershell
python simulate_vps_deployment.py
```

This will:
- ✓ Check all dependencies
- ✓ Start the server
- ✓ Run all test suites
- ✓ Generate deployment readiness report

---

## 📁 Test Files Overview

### 1. `.api-keys.test.json` - Test API Configuration
Production-like API key configuration for testing.

**Contains:**
- Super user key for admin endpoints
- Valid API key for general testing
- Inactive API key for testing authorization
- Rate-limited API key for testing limits
- Low rate limits (5/min, 20/hr) for quick testing

### 2. `test_vps_simulation.py` - Comprehensive Test Suite
**Tests:** Authentication, Rate Limiting, HTML Conversion, Error Handling, Admin Endpoints

**Run:**
```powershell
# Make sure server is running first!
python test_vps_simulation.py
```

**What it tests:**
- ✓ Public endpoints (/, /health, /version)
- ✓ Authentication (missing, invalid, inactive, valid API keys)
- ✓ Super user authorization
- ✓ Rate limiting (per-minute and per-hour)
- ✓ HTML conversion (simple, styled, with CSS, broken HTML)
- ✓ Large documents (1000 paragraphs)
- ✓ Different page sizes (A4, Letter, Legal, A3)
- ✓ Custom margins and viewports
- ✓ Error handling (missing fields, invalid data)
- ✓ Special characters and Unicode
- ✓ Admin endpoints

**Expected Output:**
```
✓ Passed: 35+
✗ Failed: 0
✅ ALL TESTS PASSED!
🚀 API is ready for production deployment!
```

### 3. `test_load_performance.py` - Load & Performance Testing
**Tests:** Throughput, Concurrent Requests, Response Times, Server Stability

**Run:**
```powershell
python test_load_performance.py
```

**What it tests:**
- Sequential requests (10 simple, 5 medium, 3 large)
- Concurrent requests (3-5 workers)
- Response time statistics (min, max, mean, median, std dev)
- Throughput (requests/second)
- PDF size consistency
- Optional stress test (20 concurrent requests)

**Metrics measured:**
- Total requests processed
- Success/failure rate
- Response times (min/max/mean/median)
- Throughput (requests/sec)
- PDF file sizes
- Server stability under load

### 4. `test_simple_api.py` - Quick Sanity Check
**Tests:** Basic API functionality

**Run:**
```powershell
python test_simple_api.py
```

Simple test to verify the API is working. Use this for quick checks.

### 5. `simulate_vps_deployment.py` - Full Deployment Simulation
**Tests:** Complete deployment workflow

**Run:**
```powershell
python simulate_vps_deployment.py
```

**What it does:**
1. Sets up test environment
2. Checks all dependencies
3. Starts Flask server automatically
4. Runs all test suites
5. Generates deployment readiness report
6. Cleans up after tests

---

## 🧪 Running Tests

### Option 1: Full Automated Testing (Recommended)

**Best for:** Complete pre-deployment validation

```powershell
python simulate_vps_deployment.py
```

This runs everything automatically and gives you a comprehensive report.

### Option 2: Manual Testing

**Best for:** Debugging specific issues

**Step 1:** Start the server
```powershell
python app.py
```

**Step 2:** Open a new terminal and run tests
```powershell
# Comprehensive tests
python test_vps_simulation.py

# Load tests
python test_load_performance.py

# Quick test
python test_simple_api.py
```

### Option 3: Individual Test Categories

Test specific features:

```powershell
# Test authentication only
python -c "from test_vps_simulation import test_authentication; test_authentication()"

# Test rate limiting only
python -c "from test_vps_simulation import test_rate_limiting; test_rate_limiting()"

# Test HTML conversion only
python -c "from test_vps_simulation import test_html_conversion; test_html_conversion()"
```

---

## 📊 Test Coverage

### Authentication & Authorization ✓
- [x] Public endpoints accessible without auth
- [x] Protected endpoints require API key
- [x] Invalid API keys rejected (403)
- [x] Inactive API keys rejected (403)
- [x] Valid API keys accepted (200)
- [x] Super user endpoints require super key
- [x] Invalid super user keys rejected (403)
- [x] Valid super user keys accepted (200)

### Rate Limiting ✓
- [x] Per-minute limits enforced (5 requests/min)
- [x] Per-hour limits enforced (20 requests/hr)
- [x] Rate limit exceeded returns 429
- [x] Rate limit resets after time window
- [x] Different keys have separate rate limits

### HTML Conversion ✓
- [x] Simple HTML converts successfully
- [x] HTML with inline CSS styles
- [x] HTML with separate CSS parameter
- [x] Broken/malformed HTML handled gracefully
- [x] Large documents (1000+ elements)
- [x] Different page sizes (A4, Letter, Legal, A3)
- [x] Custom margins
- [x] Custom viewport dimensions
- [x] Special characters (&, <, >, ", ', ©, ®)
- [x] Unicode characters (Chinese, Arabic, emoji)

### Error Handling ✓
- [x] Missing HTML content returns 400
- [x] Empty HTML returns 400
- [x] Missing JSON body returns 400
- [x] Non-existent endpoints return 404
- [x] Proper error messages in responses

### Performance ✓
- [x] Sequential request handling
- [x] Concurrent request handling
- [x] Response time consistency
- [x] Throughput measurement
- [x] Server stability under load
- [x] Memory efficiency

### Admin Endpoints ✓
- [x] List API keys (GET /admin/keys)
- [x] View rate limit config (GET /admin/rate-limit)
- [x] Super user authorization required

---

## ✅ Before Deployment Checklist

### 1. Run All Tests

```powershell
python simulate_vps_deployment.py
```

**Expected:** All tests pass ✓

### 2. Review Test Results

Check the summary output:
- [ ] All authentication tests passed
- [ ] All rate limiting tests passed
- [ ] All HTML conversion tests passed
- [ ] All error handling tests passed
- [ ] All admin endpoint tests passed
- [ ] Load tests show acceptable performance

### 3. Generate Production API Keys

```powershell
# Create super user key
python generate_api_key.py add-super-user "Production Super User"

# Create API keys for clients
python generate_api_key.py add "Production Client 1"
python generate_api_key.py add "Production Client 2"
```

### 4. Update Configuration

**Production `.api-keys.json`:**
```json
{
  "super_user": {
    "key": "your-production-super-user-key",
    "name": "Production Super User",
    "created": "2026-01-06"
  },
  "api_keys": [
    {
      "key": "your-production-api-key",
      "name": "Production Client",
      "created": "2026-01-06",
      "active": true
    }
  ],
  "rate_limit": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000
  }
}
```

**Note:** Use higher rate limits for production!

### 5. Security Checklist

- [ ] Test API keys removed from `.api-keys.json`
- [ ] Production API keys generated
- [ ] `.api-keys.json` in `.gitignore`
- [ ] API keys stored securely
- [ ] Rate limits set appropriately
- [ ] HTTPS configured on VPS
- [ ] Firewall rules configured

### 6. Performance Expectations

Based on load tests, expect:
- **Simple HTML:** ~1-2 seconds per request
- **Medium HTML:** ~2-4 seconds per request
- **Large HTML:** ~4-8 seconds per request
- **Throughput:** 2-5 requests/sec (sequential)
- **Concurrent:** 1-3 requests/sec with 3-5 workers

**If performance is slower:**
- Increase VPS resources (CPU/RAM)
- Adjust rate limits
- Consider caching for repeated conversions

### 7. Deployment

Follow [DEPLOYMENT.md](DEPLOYMENT.md) for VPS deployment instructions.

### 8. Post-Deployment Testing

After deploying to VPS, test the production endpoint:

```powershell
# Update test_production.py with your production URL
# Then run:
python test_production.py
```

---

## 🔍 Troubleshooting

### Server Won't Start

**Error:** `Address already in use`
```powershell
# Kill existing Python processes
taskkill /F /IM python.exe

# Wait a few seconds
Start-Sleep -Seconds 2

# Start server
python app.py
```

### Playwright Browser Not Found

**Error:** `Executable doesn't exist`
```powershell
playwright install chromium
```

### Test Timeouts

If tests timeout:
1. Increase timeout in test files (default: 60s)
2. Check server is running: `http://localhost:5000/health`
3. Check for errors in server console

### Rate Limit Tests Fail

If rate limiting tests fail:
1. Ensure `.api-keys.json` has low limits (5/min, 20/hr)
2. Wait 60+ seconds between test runs
3. Restart server to clear rate limit cache

### Tests Pass Locally But Fail on VPS

Common issues:
1. **Missing dependencies:** Run `pip install -r requirements.txt` on VPS
2. **Playwright not installed:** Run `playwright install chromium` on VPS
3. **Port conflicts:** Ensure port 5000 is available
4. **Firewall:** Check VPS firewall allows connections
5. **Memory:** Ensure sufficient RAM (minimum 1GB recommended)

---

## 📈 Performance Tuning

### For VPS Deployment

**Minimum Requirements:**
- 1 CPU core
- 1GB RAM
- 10GB storage

**Recommended:**
- 2 CPU cores
- 2GB RAM
- 20GB storage

**Optimal:**
- 4 CPU cores
- 4GB RAM
- 50GB storage

### Gunicorn Configuration

For production, use Gunicorn with multiple workers:

```bash
# Single worker (safe for low traffic)
gunicorn -w 1 -b 0.0.0.0:5000 app:app

# Multiple workers (better performance)
gunicorn -w 4 -b 0.0.0.0:5000 app:app --timeout 120
```

**Workers calculation:** `2 * CPU_CORES + 1`

### Rate Limiting

Adjust based on your VPS capacity:

| VPS Tier | Requests/Min | Requests/Hour |
|----------|--------------|---------------|
| Small    | 10           | 200           |
| Medium   | 60           | 1000          |
| Large    | 120          | 5000          |

---

## 🎯 Success Criteria

Your API is ready for deployment when:

- ✅ All test suites pass without errors
- ✅ Authentication works correctly
- ✅ Rate limiting enforces limits
- ✅ HTML conversions are successful
- ✅ Error handling is graceful
- ✅ Performance meets expectations
- ✅ Load tests show stability
- ✅ Production API keys generated
- ✅ Security checklist completed

Run the final check:

```powershell
python simulate_vps_deployment.py
```

Look for this message:
```
✅ ALL TESTS PASSED!
🚀 API is ready for production deployment!
```

---

## 📞 Support

If you encounter issues:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review server logs for errors
3. Verify all dependencies are installed
4. Ensure Playwright browsers are installed
5. Check [DEPLOYMENT.md](DEPLOYMENT.md) for VPS-specific issues

---

**Good luck with your deployment! 🚀**
