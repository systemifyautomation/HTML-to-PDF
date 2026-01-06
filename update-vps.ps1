# HTML-to-PDF VPS Quick Update Script
# Simple file upload method - no git required
# Run this from your Windows machine to update the production VPS

param(
    [string]$VPS = "root@htmltopdf.systemifyautomation.com",
    [switch]$SkipBackup,
    [switch]$UpdateDeps,
    [switch]$Auto
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   HTML-to-PDF VPS Update Script       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Confirm unless -Auto is used
if (-not $Auto) {
    $confirm = Read-Host "Update VPS with local changes? (y/n)"
    if ($confirm -ne "y") {
    Write-Host "Update cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "1️⃣  Uploading modified files..." -ForegroundColor Green

try {
    # Upload core files
    Write-Host "   Uploading app.py..."
    scp "$LocalPath\app.py" "${VPSUser}@${VPSHost}:${VPSPath}/app.py"
    
    Write-Host "   Uploading requirements.txt..."
    scp "$LocalPath\requirements.txt" "${VPSUser}@${VPSHost}:${VPSPath}/requirements.txt"
    
    Write-Host "   Uploading documentation..."
    scp "$LocalPath\RENDERING_IMPROVEMENTS.md" "${VPSUser}@${VPSHost}:${VPSPath}/"
    scp "$LocalPath\IMPROVEMENTS_SUMMARY.md" "${VPSUser}@${VPSHost}:${VPSPath}/"
    scp "$LocalPath\VPS_UPDATE_GUIDE.md" "${VPSUser}@${VPSHost}:${VPSPath}/"
    scp "$LocalPath\BROWSER_LIKE_RENDERING.md" "${VPSUser}@${VPSHost}:${VPSPath}/"
    scp "$LocalPath\HTML_ERRORS_FIXED.md" "${VPSUser}@${VPSHost}:${VPSPath}/"
    scp "$LocalPath\QUICK_START_ERROR_HANDLING.md" "${VPSUser}@${VPSHost}:${VPSPath}/"
    scp "$LocalPath\BEFORE_AFTER_COMPARISON.md" "${VPSUser}@${VPSHost}:${VPSPath}/"
    
    Write-Host "   Uploading examples..."
    scp "$LocalPath\examples\enhanced_usage_example.py" "${VPSUser}@${VPSHost}:${VPSPath}/examples/"
    
    Write-Host "   Uploading test scripts..."
    scp "$LocalPath\test_improvements.py" "${VPSUser}@${VPSHost}:${VPSPath}/"
    scp "$LocalPath\test_broken_html.py" "${VPSUser}@${VPSHost}:${VPSPath}/"
    
    Write-Host "   Uploading update script..."
    scp "$LocalPath\update-vps.sh" "${VPSUser}@${VPSHost}:${VPSPath}/"
    
    Write-Host "✅ Files uploaded successfully" -ForegroundColor Green
}
catch {
    Write-Host "❌ File upload failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2️⃣  Restarting Docker container on VPS..." -ForegroundColor Green

try {
    # Execute update commands on VPS
    $commands = @"
cd $VPSPath && \
echo '📦 Stopping container...' && \
docker-compose down && \
echo '🔨 Rebuilding image...' && \
docker-compose build --no-cache && \
echo '🚀 Starting container...' && \
docker-compose up -d && \
echo '⏳ Waiting for service...' && \
sleep 5 && \
echo '✅ Checking status...' && \
docker-compose ps && \
echo '🧪 Testing API...' && \
curl -s http://localhost:5000/ | head -20
"@

    ssh "${VPSUser}@${VPSHost}" $commands
    
    Write-Host "✅ Container restarted successfully" -ForegroundColor Green
}
catch {
    Write-Host "❌ Container restart failed: $_" -ForegroundColor Red
    Write-Host "⚠️  You may need to SSH manually and check logs" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "3️⃣  Testing public endpoint..." -ForegroundColor Green

try {
    $response = Invoke-RestMethod -Uri "https://${VPSHost}/" -Method Get -TimeoutSec 10
    
    if ($response.improvements) {
        Write-Host "✅ API responding with new features!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 New improvements detected:" -ForegroundColor Cyan
        $response.usage.improvements | ForEach-Object { Write-Host "   • $_" -ForegroundColor White }
    }
    else {
        Write-Host "⚠️  API responding but improvements not detected" -ForegroundColor Yellow
        Write-Host "   This might be normal if the update is still processing" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️  Could not test public endpoint: $_" -ForegroundColor Yellow
    Write-Host "   This might be normal if using different ports or SSL" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ UPDATE COMPLETE!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Test your API: https://${VPSHost}/convert" -ForegroundColor White
Write-Host "   2. View logs: ssh ${VPSUser}@${VPSHost} 'cd $VPSPath && docker-compose logs -f'" -ForegroundColor White
Write-Host "   3. Check status: ssh ${VPSUser}@${VPSHost} 'cd $VPSPath && docker-compose ps'" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Test with new parameters:" -ForegroundColor Yellow
Write-Host @"
   curl -X POST https://${VPSHost}/convert \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-key" \
     -d '{
       "html": "<h1>Test</h1>",
       "page_size": "Letter",
       "margin": "1in",
       "optimize": true
     }' \
     --output test.pdf
"@ -ForegroundColor White
Write-Host ""
Write-Host "📖 Documentation: $VPSPath/RENDERING_IMPROVEMENTS.md" -ForegroundColor Yellow
Write-Host ""
