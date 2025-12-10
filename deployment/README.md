# Deployment Directory

This directory contains configuration files and scripts for deploying the HTML-to-PDF Converter API to production servers.

## Files

### `htmltopdf.service`
Systemd service file for running the application as a background service on Linux servers.

**Usage:**
```bash
# Copy to systemd directory (adjust paths first!)
sudo cp htmltopdf.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable htmltopdf
sudo systemctl start htmltopdf
```

### `nginx.conf`
Nginx reverse proxy configuration for SSL/TLS termination and load balancing.

**Usage:**
```bash
# Copy to Nginx sites-available
sudo cp nginx.conf /etc/nginx/sites-available/htmltopdf

# Enable site
sudo ln -s /etc/nginx/sites-available/htmltopdf /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### `deploy.sh`
Automated deployment script for updating the application on the server.

**Usage:**
```bash
# Make executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## Quick Reference

### VPS Details
- **URL:** htmltopdf.systemifyautomation.com:9000
- **Port:** 9000
- **Service Name:** htmltopdf

### Common Commands
```bash
# View logs
sudo journalctl -u htmltopdf -f

# Restart service
sudo systemctl restart htmltopdf

# Check status
sudo systemctl status htmltopdf

# Update application
cd /path/to/HTML-to-PDF && ./deployment/deploy.sh
```

## Important Notes

⚠️ **Before deploying:**
1. Update paths in `htmltopdf.service` to match your VPS setup
2. Replace `your-username` with your actual username
3. Ensure Python virtual environment is created and dependencies installed
4. Test the configuration before enabling the service

See `DEPLOYMENT.md` in the root directory for complete deployment instructions.
