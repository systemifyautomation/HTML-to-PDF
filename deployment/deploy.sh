#!/bin/bash

# HTML-to-PDF Deployment Script for Hostinger VPS
# This script automates the deployment process

set -e  # Exit on error

echo "🚀 HTML-to-PDF Deployment Script"
echo "================================"

# Configuration
APP_DIR="/home/$(whoami)/apps/HTML-to-PDF"
SERVICE_NAME="htmltopdf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if running on the server
if [ ! -d "$APP_DIR" ]; then
    print_error "Application directory not found: $APP_DIR"
    echo "Please run this script on your VPS"
    exit 1
fi

# Navigate to application directory
cd "$APP_DIR"
print_success "Changed to application directory"

# Pull latest changes
print_info "Pulling latest changes from repository..."
git pull origin main
print_success "Code updated"

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Update dependencies
print_info "Updating dependencies..."
pip install -r requirements.txt --upgrade
print_success "Dependencies updated"

# Install/update Playwright browsers
print_info "Updating Playwright browsers..."
playwright install chromium
print_success "Playwright browsers updated"

# Restart the service
print_info "Restarting service..."
sudo systemctl restart "$SERVICE_NAME"
sleep 2

# Check service status
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_success "Service restarted successfully"
    
    # Test the endpoint
    print_info "Testing health endpoint..."
    if curl -f http://localhost:9000/health > /dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        print_info "Checking service logs..."
        sudo journalctl -u "$SERVICE_NAME" -n 20
        exit 1
    fi
else
    print_error "Service failed to start"
    print_info "Service status:"
    sudo systemctl status "$SERVICE_NAME"
    print_info "Recent logs:"
    sudo journalctl -u "$SERVICE_NAME" -n 50
    exit 1
fi

echo ""
print_success "Deployment completed successfully!"
echo ""
echo "Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager -l
echo ""
print_info "To view logs, run: sudo journalctl -u $SERVICE_NAME -f"
