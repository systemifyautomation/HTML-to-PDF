#!/bin/bash

# SSL Setup Script for HTML-to-PDF API
# This script sets up Nginx with Let's Encrypt SSL certificate

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔒 SSL Setup for HTML-to-PDF API${NC}"
echo "=================================="
echo ""

# Configuration
DOMAIN="htmltopdf.systemifyautomation.com"
APP_DIR="$HOME/HTML-to-PDF"
NGINX_CONF="/etc/nginx/sites-available/htmltopdf"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run with sudo${NC}"
    exit 1
fi

echo -e "${YELLOW}→ Installing Nginx and Certbot...${NC}"
apt update
apt install -y nginx certbot python3-certbot-nginx

echo -e "${GREEN}✓ Nginx and Certbot installed${NC}"

echo -e "${YELLOW}→ Copying Nginx configuration...${NC}"
cp "$APP_DIR/deployment/nginx.conf" "$NGINX_CONF"

echo -e "${GREEN}✓ Nginx configuration copied${NC}"

echo -e "${YELLOW}→ Enabling site...${NC}"
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/htmltopdf

# Remove default site if it exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
    echo -e "${GREEN}✓ Removed default site${NC}"
fi

echo -e "${YELLOW}→ Testing Nginx configuration...${NC}"
nginx -t

echo -e "${YELLOW}→ Restarting Nginx...${NC}"
systemctl restart nginx
systemctl enable nginx

echo -e "${GREEN}✓ Nginx is running${NC}"

echo ""
echo -e "${YELLOW}→ Obtaining SSL certificate from Let's Encrypt...${NC}"
echo -e "${YELLOW}   You will be asked for your email address${NC}"
echo ""

# Get SSL certificate
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email || \
certbot --nginx -d "$DOMAIN"

echo ""
echo -e "${GREEN}✓ SSL certificate obtained and configured!${NC}"

echo -e "${YELLOW}→ Setting up automatic certificate renewal...${NC}"
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ SSL Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Your API is now accessible at:"
echo -e "${GREEN}https://$DOMAIN${NC}"
echo ""
echo "Test your secure endpoint:"
echo -e "${YELLOW}curl https://$DOMAIN/health${NC}"
echo ""
echo "Certificate will auto-renew before expiration."
echo "Check renewal timer: systemctl status certbot.timer"
