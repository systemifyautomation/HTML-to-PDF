# HTML-to-PDF VPS Quick Update Script
# Simple file upload method - no git required
# Updates htmltopdf.systemifyautomation.com with local changes

param(
    [string]$VPS = "root@htmltopdf.systemifyautomation.com",
    [switch]$SkipBackup,
    [switch]$UpdateDeps,
    [switch]$Auto
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  HTML-to-PDF VPS Update Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Confirm unless -Auto is used
if (-not $Auto) {
    $confirm = Read-Host "Update VPS with local changes? (y/n)"
    if ($confirm -ne "y") {
        Write-Host "Update cancelled" -ForegroundColor Red
        exit 0
    }
}

# Step 1: Backup API keys (unless skipped)
if (-not $SkipBackup) {
    Write-Host "Backing up API keys..." -ForegroundColor Yellow
    ssh $VPS "cp /opt/html-to-pdf/.api-keys.json /root/.api-keys-backup-`$(date +%Y%m%d-%H%M%S).json && echo 'Backup created'" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "API keys backed up" -ForegroundColor Green
    } else {
        Write-Host "Backup skipped (may not exist yet)" -ForegroundColor Yellow
    }
}

# Step 2: Upload files
Write-Host "`nUploading updated files..." -ForegroundColor Yellow
scp app.py version.json ${VPS}:/opt/html-to-pdf/
if ($LASTEXITCODE -ne 0) {
    Write-Host "Upload failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Files uploaded successfully" -ForegroundColor Green

# Step 3: Update dependencies if requested
if ($UpdateDeps) {
    Write-Host "`nUpdating Python dependencies..." -ForegroundColor Yellow
    scp requirements.txt ${VPS}:/opt/html-to-pdf/
    ssh $VPS "cd /opt/html-to-pdf && source venv/bin/activate && pip install -r requirements.txt"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencies updated" -ForegroundColor Green
    } else {
        Write-Host "Dependency update had issues, continuing..." -ForegroundColor Yellow
    }
}

# Step 4: Restart service
Write-Host "`nRestarting service..." -ForegroundColor Yellow
ssh $VPS "systemctl restart html-to-pdf && sleep 3"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Service restart failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Service restarted" -ForegroundColor Green

# Step 5: Check service status
Write-Host "`nService status..." -ForegroundColor Yellow
ssh $VPS "systemctl status html-to-pdf --no-pager | head -15"

# Step 6: Verify version
Write-Host "`nVerifying update..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://htmltopdf.systemifyautomation.com/version" -Method Get -TimeoutSec 10
    Write-Host "Version: $($response.version)" -ForegroundColor Cyan
    Write-Host "Updated: $($response.updated_at)" -ForegroundColor Cyan
    
    if ($response.changelog -and $response.changelog.Count -gt 0) {
        Write-Host "`nRecent changes:" -ForegroundColor Cyan
        $response.changelog | Select-Object -First 3 | ForEach-Object { Write-Host "  • $_" -ForegroundColor White }
    }
} catch {
    Write-Host "Could not fetch version info (check manually)" -ForegroundColor Yellow
}

# Success message
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Update completed successfully!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Test your endpoint:" -ForegroundColor Cyan
Write-Host "  curl https://htmltopdf.systemifyautomation.com/health" -ForegroundColor White
Write-Host "  curl https://htmltopdf.systemifyautomation.com/version`n" -ForegroundColor White

# Usage instructions
Write-Host "Usage examples:" -ForegroundColor DarkGray
Write-Host "  .\update-vps-simple.ps1                    # Standard update" -ForegroundColor DarkGray
Write-Host "  .\update-vps-simple.ps1 -UpdateDeps        # Update with dependencies" -ForegroundColor DarkGray
Write-Host "  .\update-vps-simple.ps1 -SkipBackup        # Skip API key backup" -ForegroundColor DarkGray
Write-Host "  .\update-vps-simple.ps1 -Auto              # No confirmation prompt`n" -ForegroundColor DarkGray
