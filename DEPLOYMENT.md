# Deployment Guide - Hostinger VPS

This guide covers deploying the HTML-to-PDF Converter API to your Hostinger VPS at `htmltopdf.systemifyautomation.com:9000`.

## 📋 Prerequisites

- Hostinger VPS with SSH access
- Domain configured: `htmltopdf.systemifyautomation.com`
- Python 3.8+ installed on VPS
- Virtual environment created on VPS
- Git installed on VPS

## 🚀 Deployment Steps

### 1. Connect to Your VPS

```bash
ssh your-username@htmltopdf.systemifyautomation.com
```

### 2. Install System Dependencies

```bash
# Update package list
sudo apt-get update

# Install WeasyPrint dependencies
sudo apt-get install -y python3-dev python3-pip python3-setuptools python3-wheel \
    python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Install git if not present
sudo apt-get install -y git
```

### 3. Clone the Repository

```bash
# Navigate to your preferred directory
cd /home/your-username/apps  # Adjust path as needed

# Clone the repository
git clone https://github.com/systemifyautomation/HTML-to-PDF.git
cd HTML-to-PDF
```

### 4. Set Up Python Virtual Environment

```bash
# Create virtual environment if not exists
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add the following content:
```env
FLASK_ENV=production
PORT=9000
HOST=0.0.0.0
MAX_CONTENT_LENGTH=16777216
LOG_LEVEL=INFO
```

### 6. Test the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the application
python app.py
```

Test from another terminal:
```bash
curl http://localhost:9000/health
```

If successful, press `Ctrl+C` to stop the test server.

### 7. Set Up Systemd Service (Run as Background Service)

```bash
# Create systemd service file
sudo nano /etc/systemd/system/htmltopdf.service
```

Copy the contents from `deployment/htmltopdf.service` (see below), adjusting paths:

```ini
[Unit]
Description=HTML to PDF Converter API
After=network.target

[Service]
Type=exec
User=your-username
Group=your-username
WorkingDirectory=/home/your-username/apps/HTML-to-PDF
Environment="PATH=/home/your-username/apps/HTML-to-PDF/venv/bin"
ExecStart=/home/your-username/apps/HTML-to-PDF/venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Important**: Replace `your-username` and adjust paths to match your VPS setup.

### 8. Enable and Start the Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable htmltopdf

# Start the service
sudo systemctl start htmltopdf

# Check status
sudo systemctl status htmltopdf
```

### 9. Configure Firewall (if applicable)

```bash
# Allow port 9000
sudo ufw allow 9000/tcp
sudo ufw reload
```

### 10. Test the Deployment

```bash
# From your VPS
curl http://localhost:9000/health

# From your local machine
curl http://htmltopdf.systemifyautomation.com:9000/health
```

## 🔄 Updating the Application

To pull the latest changes and restart:

```bash
# Navigate to app directory
cd /home/your-username/apps/HTML-to-PDF

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies (if requirements.txt changed)
pip install -r requirements.txt

# Restart the service
sudo systemctl restart htmltopdf

# Check status
sudo systemctl status htmltopdf
```

## 🔧 Useful Commands

### View Logs
```bash
# View service logs
sudo journalctl -u htmltopdf -f

# View last 100 lines
sudo journalctl -u htmltopdf -n 100
```

### Service Management
```bash
# Start service
sudo systemctl start htmltopdf

# Stop service
sudo systemctl stop htmltopdf

# Restart service
sudo systemctl restart htmltopdf

# Check status
sudo systemctl status htmltopdf

# Disable service (won't start on boot)
sudo systemctl disable htmltopdf
```

## 🔒 Security Recommendations

1. **Firewall**: Only allow necessary ports (SSH, 9000)
2. **HTTPS**: Consider setting up nginx reverse proxy with SSL/TLS
3. **Authentication**: Add API key authentication if needed
4. **Rate Limiting**: Implement rate limiting for production use
5. **Updates**: Keep system and dependencies updated

## 🌐 Optional: Nginx Reverse Proxy with SSL

For production, it's recommended to use Nginx as a reverse proxy with SSL:

```bash
# Install Nginx and Certbot
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/htmltopdf
```

Add configuration:
```nginx
server {
    listen 80;
    server_name htmltopdf.systemifyautomation.com;

    location / {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 16M;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/htmltopdf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d htmltopdf.systemifyautomation.com
```

## 📊 Monitoring

Monitor your application:
```bash
# Check if service is running
systemctl is-active htmltopdf

# Monitor system resources
htop

# Check port
sudo netstat -tulpn | grep 9000
```

## 🆘 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u htmltopdf -n 50

# Check if port is already in use
sudo lsof -i :9000

# Check permissions
ls -la /home/your-username/apps/HTML-to-PDF
```

### Application errors
```bash
# Test manually
source venv/bin/activate
python app.py

# Check Python path
which python
```

### Connection refused
```bash
# Check if service is running
sudo systemctl status htmltopdf

# Check firewall
sudo ufw status

# Test locally first
curl http://localhost:9000/health
```

## 📞 Support

For issues or questions, please open an issue on the GitHub repository.
