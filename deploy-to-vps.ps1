# PowerShell Script to Deploy HTML-to-PDF to Hostinger VPS
# Usage: .\deploy-to-vps.ps1 -VPS_USER "root" -VPS_HOST "htmltopdf.systemifyautomation.com"

param(
    [Parameter(Mandatory=$true)]
    [string]$VPS_USER,
    
    [Parameter(Mandatory=$true)]
    [string]$VPS_HOST,
    
    [Parameter(Mandatory=$false)]
    [string]$APP_PATH = "/opt/html-to-pdf"
)

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  HTML-to-PDF VPS Deployment Script" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$SSH_TARGET = "$VPS_USER@$VPS_HOST"

# Function to run SSH command
function Invoke-SSHCommand {
    param([string]$Command)
    ssh $SSH_TARGET $Command
}

# Function to upload file via SCP
function Copy-ToVPS {
    param(
        [string]$LocalPath,
        [string]$RemotePath
    )
    scp $LocalPath "${SSH_TARGET}:${RemotePath}"
}

Write-Host "Target: $SSH_TARGET" -ForegroundColor Yellow
Write-Host "App Path: $APP_PATH`n" -ForegroundColor Yellow

# Step 1: Test connection
Write-Host "Step 1: Testing SSH connection..." -ForegroundColor Green
$connectionTest = ssh -o ConnectTimeout=5 $SSH_TARGET "echo 'Connected'"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAILED] Could not connect to VPS. Check your credentials." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Connection successful`n" -ForegroundColor Green

# Step 2: Check if application exists
Write-Host "Step 2: Checking existing installation..." -ForegroundColor Green
$appExists = Invoke-SSHCommand "test -d $APP_PATH; echo `$?"
if ($appExists -eq "0") {
    Write-Host "[WARNING] Application already exists at $APP_PATH" -ForegroundColor Yellow
    $confirm = Read-Host "Do you want to update it? (y/n)"
    if ($confirm -ne "y") {
        Write-Host "Deployment cancelled." -ForegroundColor Red
        exit 0
    }
    $isUpdate = $true
} else {
    $isUpdate = $false
    Write-Host "[OK] New installation`n" -ForegroundColor Green
}

# Step 3: Create application directory
if (-not $isUpdate) {
    Write-Host "Step 3: Creating application directory..." -ForegroundColor Green
    Invoke-SSHCommand "mkdir -p $APP_PATH"
    Write-Host "[OK] Directory created`n" -ForegroundColor Green
} else {
    Write-Host "Step 3: Skipping directory creation (update mode)`n" -ForegroundColor Yellow
}

# Step 4: Upload application files
Write-Host "Step 4: Uploading application files..." -ForegroundColor Green
$filesToUpload = @(
    "app.py",
    "requirements.txt",
    "generate_api_key.py",
    "runtime.txt"
)

foreach ($file in $filesToUpload) {
    if (Test-Path $file) {
        Write-Host "  Uploading $file..." -ForegroundColor Gray
        Copy-ToVPS -LocalPath $file -RemotePath "$APP_PATH/$file"
    }
}

# Upload examples directory if exists
if (Test-Path "examples") {
    Write-Host "  Uploading examples directory..." -ForegroundColor Gray
    scp -r examples "${SSH_TARGET}:${APP_PATH}/" 2>$null
}

Write-Host "[OK] Files uploaded`n" -ForegroundColor Green

# Step 5: Check for API keys
Write-Host "Step 5: Checking API keys configuration..." -ForegroundColor Green
if (Test-Path ".api-keys.json") {
    $uploadKeys = Read-Host "Found .api-keys.json locally. Upload to VPS? (y/n)"
    if ($uploadKeys -eq "y") {
        Copy-ToVPS -LocalPath ".api-keys.json" -RemotePath "$APP_PATH/.api-keys.json"
        Write-Host "[OK] API keys uploaded`n" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Skipped API keys upload`n" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARNING] No .api-keys.json found locally" -ForegroundColor Yellow
    Write-Host "  Remember to create API keys on the VPS!`n" -ForegroundColor Yellow
}

# Step 6: Create/update .env file
Write-Host "Step 6: Creating environment configuration..." -ForegroundColor Green
Invoke-SSHCommand "cat > $APP_PATH/.env << 'EOF'
FLASK_ENV=production
PORT=5000
HOST=127.0.0.1
MAX_CONTENT_LENGTH=16777216
LOG_LEVEL=INFO
EOF"
Write-Host "[OK] Environment file created`n" -ForegroundColor Green

# Step 7: Install dependencies
Write-Host "Step 7: Installing dependencies on VPS..." -ForegroundColor Green
Write-Host "  This may take a few minutes..." -ForegroundColor Gray

Invoke-SSHCommand "cd $APP_PATH; python3 -m venv venv; source venv/bin/activate; pip install --upgrade pip; pip install -r requirements.txt; playwright install chromium"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dependencies installed`n" -ForegroundColor Green
} else {
    Write-Host "[FAILED] Could not install dependencies`n" -ForegroundColor Red
    Write-Host "Try running manually: ssh $SSH_TARGET" -ForegroundColor Yellow
    exit 1
}

# Step 8: Create systemd service
Write-Host "Step 8: Setting up systemd service..." -ForegroundColor Green

Invoke-SSHCommand "sudo tee /etc/systemd/system/html-to-pdf.service > /dev/null << 'EOF'
[Unit]
Description=HTML-to-PDF Converter API
After=network.target

[Service]
Type=simple
User=$VPS_USER
WorkingDirectory=$APP_PATH
Environment=PATH=$APP_PATH/venv/bin
ExecStart=$APP_PATH/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --timeout 120 --access-logfile /var/log/html-to-pdf-access.log --error-logfile /var/log/html-to-pdf-error.log app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

# Create log files
Invoke-SSHCommand "sudo touch /var/log/html-to-pdf-access.log /var/log/html-to-pdf-error.log; sudo chown ${VPS_USER}:${VPS_USER} /var/log/html-to-pdf-*.log"

# Enable and start service
Invoke-SSHCommand "sudo systemctl daemon-reload; sudo systemctl enable html-to-pdf; sudo systemctl restart html-to-pdf"

Write-Host "[OK] Service configured and started`n" -ForegroundColor Green

# Step 9: Check service status
Write-Host "Step 9: Verifying service status..." -ForegroundColor Green
Start-Sleep -Seconds 3
$serviceStatus = Invoke-SSHCommand "sudo systemctl is-active html-to-pdf"
if ($serviceStatus -eq "active") {
    Write-Host "[OK] Service is running!`n" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Service may not be running" -ForegroundColor Yellow
    Write-Host "  Check logs: ssh $SSH_TARGET 'sudo journalctl -u html-to-pdf -n 50'`n" -ForegroundColor Yellow
}

# Step 10: Test health endpoint
Write-Host "Step 10: Testing health endpoint..." -ForegroundColor Green
Start-Sleep -Seconds 2
$healthCheck = Invoke-SSHCommand "curl -s http://localhost:5000/health"
if ($healthCheck -like "*healthy*") {
    Write-Host "[OK] Health check passed!`n" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Health check did not return expected response" -ForegroundColor Yellow
    Write-Host "Response: $healthCheck`n" -ForegroundColor Gray
}

# Summary
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Configure Nginx reverse proxy" -ForegroundColor White
Write-Host "2. Set up SSL certificate with certbot" -ForegroundColor White
Write-Host "3. Test API from external network" -ForegroundColor White
Write-Host "4. Integrate with n8n workflows`n" -ForegroundColor White

Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  Check status:  ssh $SSH_TARGET 'sudo systemctl status html-to-pdf'" -ForegroundColor Gray
Write-Host "  View logs:     ssh $SSH_TARGET 'sudo journalctl -u html-to-pdf -f'" -ForegroundColor Gray
Write-Host "  Restart:       ssh $SSH_TARGET 'sudo systemctl restart html-to-pdf'`n" -ForegroundColor Gray

Write-Host "Deployment successful!`n" -ForegroundColor Green
