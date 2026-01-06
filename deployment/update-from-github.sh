#!/bin/bash
set -e

# HTML-to-PDF Update Script
# This script pulls the latest changes from GitHub and updates the production service

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/html-to-pdf"
SERVICE_NAME="html-to-pdf"

echo -e "${YELLOW}╔════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║   HTML-to-PDF Update from GitHub          ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (sudo)${NC}"
    exit 1
fi

# Navigate to app directory
cd $APP_DIR || { echo -e "${RED}❌ Directory $APP_DIR not found${NC}"; exit 1; }

# Stop service
echo -e "${YELLOW}⏸  Stopping service...${NC}"
systemctl stop $SERVICE_NAME

# Get current commit
CURRENT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
echo -e "${YELLOW}📍 Current commit: $CURRENT_COMMIT${NC}"

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Uncommitted local changes detected. Creating backup...${NC}"
    git stash save "auto-backup-$(date +%Y%m%d-%H%M%S)"
fi

# Pull latest changes
echo -e "${YELLOW}⬇️  Pulling from GitHub...${NC}"
if git pull origin main; then
    echo -e "${GREEN}✅ Successfully pulled latest changes${NC}"
else
    echo -e "${RED}❌ Failed to pull from GitHub${NC}"
    systemctl start $SERVICE_NAME
    exit 1
fi

NEW_COMMIT=$(git rev-parse --short HEAD)

# Check if anything changed
if [ "$CURRENT_COMMIT" = "$NEW_COMMIT" ]; then
    echo -e "${GREEN}ℹ️  Already up to date (no changes)${NC}"
else
    echo -e "${GREEN}📦 Updated from $CURRENT_COMMIT to $NEW_COMMIT${NC}"
fi

# Check if requirements.txt changed
if git diff --name-only $CURRENT_COMMIT HEAD 2>/dev/null | grep -q "requirements.txt"; then
    echo -e "${YELLOW}📦 requirements.txt changed, updating Python dependencies...${NC}"
    source venv/bin/activate || { echo -e "${RED}❌ Failed to activate venv${NC}"; exit 1; }
    pip install -r requirements.txt
    
    # Check if Playwright version changed
    if git diff $CURRENT_COMMIT HEAD requirements.txt | grep -q "playwright"; then
        echo -e "${YELLOW}🎭 Playwright version changed, reinstalling browser...${NC}"
        playwright install chromium
        
        # Install system dependencies if needed
        echo -e "${YELLOW}🔧 Checking system dependencies...${NC}"
        playwright install-deps chromium || echo -e "${YELLOW}⚠️  Some system deps may have failed (non-critical)${NC}"
    fi
fi

# Check if app.py changed
if git diff --name-only $CURRENT_COMMIT HEAD 2>/dev/null | grep -q "app.py"; then
    echo -e "${YELLOW}🔧 app.py changed${NC}"
fi

# Start service
echo -e "${YELLOW}▶️  Starting service...${NC}"
systemctl start $SERVICE_NAME

# Wait for service to initialize
sleep 3

# Check service status
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✅ Service is running${NC}"
else
    echo -e "${RED}❌ Service failed to start${NC}"
    systemctl status $SERVICE_NAME --no-pager
    exit 1
fi

# Health check
echo -e "${YELLOW}🏥 Performing health check...${NC}"
if curl -s http://localhost:5000/health | grep -q "healthy"; then
    VERSION=$(curl -s http://localhost:5000/health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ Health check passed! Version: $VERSION${NC}"
else
    echo -e "${RED}⚠️  Health check failed${NC}"
    echo -e "${YELLOW}Service status:${NC}"
    systemctl status $SERVICE_NAME --no-pager
    echo -e "${YELLOW}Recent logs:${NC}"
    journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi

# Show recent commits
echo ""
echo -e "${YELLOW}📝 Recent changes:${NC}"
git log --oneline -5

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Update completed successfully!        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Test your endpoints:"
echo -e "  Local:  curl http://localhost:5000/health"
echo -e "  HTTPS:  curl https://htmltopdf.example.com/health"
echo ""
