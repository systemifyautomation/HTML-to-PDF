# Quick Test Script for HTML-to-PDF API

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "HTML-to-PDF API - Quick Test" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Step 1: Copy test API keys
Write-Host "[1/4] Setting up test configuration..." -ForegroundColor Yellow
Copy-Item .api-keys.test.json .api-keys.json -Force
Write-Host "   Test API keys configured`n" -ForegroundColor Green

# Step 2: Stop any running servers
Write-Host "[2/4] Preparing environment..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null | Out-Null
Start-Sleep -Seconds 2
Write-Host "   Environment ready`n" -ForegroundColor Green

# Step 3: Start server
Write-Host "[3/4] Starting server..." -ForegroundColor Yellow
$job = Start-Job -ScriptBlock {
    Set-Location "C:\Users\PCZZ3\Documents\GitHub\HTML-to-PDF"
    python app.py
}
Start-Sleep -Seconds 5
Write-Host "   Server started (Job ID: $($job.Id))`n" -ForegroundColor Green

# Step 4: Run test
Write-Host "[4/4] Running API test...`n" -ForegroundColor Yellow
Write-Host "="*60 -ForegroundColor Cyan
python test_simple_api.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n"
    Write-Host "="*60 -ForegroundColor Green
    Write-Host " QUICK TEST PASSED!" -ForegroundColor Green
    Write-Host "="*60 -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "  1. Full test: python test_vps_simulation.py" -ForegroundColor White
    Write-Host "  2. Load test: python test_load_performance.py" -ForegroundColor White
    Write-Host "`nStop server: Stop-Job $($job.Id); Remove-Job $($job.Id)`n" -ForegroundColor Gray
} else {
    Write-Host "`n Test failed!`n" -ForegroundColor Red
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -ErrorAction SilentlyContinue
}
