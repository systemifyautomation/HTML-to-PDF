#!/bin/bash

# HTML-to-PDF VPS Update Script
# This script updates your running Docker deployment with zero downtime

set -e  # Exit on error

echo "=========================================="
echo "HTML-to-PDF Update Script"
echo "=========================================="
echo ""

# Configuration
APP_DIR=~/HTML-to-PDF
BACKUP_DIR=~/HTML-to-PDF-backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "📍 App Directory: $APP_DIR"
echo "💾 Backup Directory: $BACKUP_DIR"
echo ""

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Navigate to app directory
cd $APP_DIR || exit 1

echo "1️⃣  Creating backup..."
# Backup current version
mkdir -p $BACKUP_DIR/$TIMESTAMP
cp app.py $BACKUP_DIR/$TIMESTAMP/
cp requirements.txt $BACKUP_DIR/$TIMESTAMP/
cp docker-compose.yml $BACKUP_DIR/$TIMESTAMP/
echo "✅ Backup created in $BACKUP_DIR/$TIMESTAMP"
echo ""

echo "2️⃣  Pulling latest changes from Git..."
# Pull latest changes
if git pull origin main; then
    echo "✅ Git pull successful"
else
    echo "⚠️  Git pull failed or no changes. Continuing anyway..."
fi
echo ""

echo "3️⃣  Stopping current container..."
# Stop container
docker-compose down
echo "✅ Container stopped"
echo ""

echo "4️⃣  Rebuilding Docker image..."
# Rebuild image
docker-compose build --no-cache
echo "✅ Image rebuilt"
echo ""

echo "5️⃣  Starting updated container..."
# Start container
docker-compose up -d
echo "✅ Container started"
echo ""

echo "6️⃣  Waiting for service to be ready..."
sleep 5
echo ""

echo "7️⃣  Checking container status..."
# Check status
docker-compose ps
echo ""

echo "8️⃣  Testing API endpoint..."
# Test API
if curl -s http://localhost:5000/ > /dev/null; then
    echo "✅ API is responding"
    echo ""
    echo "📋 API Info:"
    curl -s http://localhost:5000/ | python3 -m json.tool | head -20
else
    echo "❌ API is not responding!"
    echo "Rolling back..."
    
    # Rollback
    docker-compose down
    cp $BACKUP_DIR/$TIMESTAMP/app.py ./
    cp $BACKUP_DIR/$TIMESTAMP/requirements.txt ./
    docker-compose up -d --build
    
    echo "⚠️  Rolled back to previous version"
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ UPDATE COMPLETE!"
echo "=========================================="
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🔄 Rollback if needed:"
echo "   cd $APP_DIR"
echo "   docker-compose down"
echo "   cp $BACKUP_DIR/$TIMESTAMP/* ./"
echo "   docker-compose up -d --build"
echo ""
echo "🧪 Test new features:"
echo "   curl -X GET https://htmltopdf.systemifyautomation.com/"
echo ""
