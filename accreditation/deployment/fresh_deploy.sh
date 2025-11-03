#!/bin/bash

# Complete Redeployment Script for PLP Accreditation System
# This script performs a fresh deployment from scratch

set -e  # Exit on error

echo "============================================"
echo "  PLP Accreditation System - Fresh Deploy"
echo "============================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
APP_NAME="plp-accreditation"
APP_DIR="/home/plpadmin/PLP-Accreditation-System"
PROJECT_DIR="$APP_DIR/accreditation"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/sh3ki/PLP-Accreditation-System.git"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run this script as root or with sudo.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Installing system dependencies...${NC}"
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx git
echo -e "${GREEN}✓ System dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 2: Creating application directory...${NC}"
mkdir -p "$APP_DIR"
chown -R plpadmin:plpadmin "$APP_DIR"
cd "$APP_DIR"
echo -e "${GREEN}✓ Directory created${NC}"
echo ""

echo -e "${YELLOW}Step 3: Cloning repository...${NC}"
if [ -d ".git" ]; then
    echo "Repository already exists, pulling latest changes..."
    sudo -u plpadmin git pull origin master
else
    cd /home/plpadmin
    rm -rf "$APP_DIR"
    sudo -u plpadmin git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi
chown -R plpadmin:plpadmin "$APP_DIR"
echo -e "${GREEN}✓ Repository cloned/updated${NC}"
echo ""

echo -e "${YELLOW}Step 4: Creating virtual environment...${NC}"
cd "$PROJECT_DIR"
sudo -u plpadmin python3 -m venv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

echo -e "${YELLOW}Step 5: Upgrading pip...${NC}"
sudo -u plpadmin $VENV_DIR/bin/pip install --upgrade pip
echo -e "${GREEN}✓ Pip upgraded${NC}"
echo ""

echo -e "${YELLOW}Step 6: Installing Python dependencies...${NC}"
sudo -u plpadmin $VENV_DIR/bin/pip install -r requirements.txt
sudo -u plpadmin $VENV_DIR/bin/pip install gunicorn
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 7: Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please create .env file with required variables:"
    echo "  - SECRET_KEY"
    echo "  - DEBUG"
    echo "  - ALLOWED_HOSTS"
    echo "  - Firebase credentials"
    echo "  - Email settings"
    exit 1
fi
echo -e "${GREEN}✓ Environment file found${NC}"
echo ""

echo -e "${YELLOW}Step 8: Collecting static files...${NC}"
sudo -u plpadmin $VENV_DIR/bin/python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

echo -e "${YELLOW}Step 9: Creating gunicorn service file...${NC}"
tee /etc/systemd/system/gunicorn.service > /dev/null << EOF
[Unit]
Description=Gunicorn daemon for PLP Accreditation System
After=network.target

[Service]
User=plpadmin
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn \\
    --workers 3 \\
    --bind 127.0.0.1:8000 \\
    --timeout 120 \\
    --access-logfile /var/log/plp_accreditation.access.log \\
    --error-logfile /var/log/plp_accreditation.err.log \\
    --log-level info \\
    accreditation.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
echo -e "${GREEN}✓ Gunicorn service created${NC}"
echo ""

echo -e "${YELLOW}Step 10: Creating nginx configuration...${NC}"
tee /etc/nginx/sites-available/plp_accreditation > /dev/null << 'EOF'
server {
    listen 80;
    server_name plpaccreditation.com www.plpaccreditation.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name plpaccreditation.com www.plpaccreditation.com;

    # SSL Configuration (update paths to your SSL certificates)
    ssl_certificate /etc/letsencrypt/live/plpaccreditation.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/plpaccreditation.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 100M;

    # Static files
    location /static/ {
        alias /home/plpadmin/PLP-Accreditation-System/accreditation/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/plpadmin/PLP-Accreditation-System/accreditation/media/;
        expires 30d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
EOF
echo -e "${GREEN}✓ Nginx configuration created${NC}"
echo ""

echo -e "${YELLOW}Step 11: Enabling nginx site...${NC}"
ln -sf /etc/nginx/sites-available/plp_accreditation /etc/nginx/sites-enabled/
nginx -t
echo -e "${GREEN}✓ Nginx configuration enabled${NC}"
echo ""

echo -e "${YELLOW}Step 12: Creating log files...${NC}"
touch /var/log/plp_accreditation.access.log
touch /var/log/plp_accreditation.err.log
chown plpadmin:www-data /var/log/plp_accreditation.*.log
echo -e "${GREEN}✓ Log files created${NC}"
echo ""

echo -e "${YELLOW}Step 13: Setting permissions...${NC}"
chown -R plpadmin:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"
echo -e "${GREEN}✓ Permissions set${NC}"
echo ""

echo -e "${YELLOW}Step 14: Reloading systemd and starting services...${NC}"
systemctl daemon-reload
systemctl enable gunicorn
systemctl start gunicorn
systemctl restart nginx
echo -e "${GREEN}✓ Services started${NC}"
echo ""

echo -e "${YELLOW}Step 15: Checking service status...${NC}"
echo ""
echo "Gunicorn status:"
systemctl status gunicorn --no-pager -l
echo ""
echo "Nginx status:"
systemctl status nginx --no-pager -l
echo ""

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Deployment completed successfully!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${YELLOW}Service URLs:${NC}"
echo "  HTTP:  http://plpaccreditation.com"
echo "  HTTPS: https://plpaccreditation.com"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  Check logs:     sudo tail -f /var/log/plp_accreditation.err.log"
echo "  Restart app:    sudo systemctl restart gunicorn"
echo "  Restart nginx:  sudo systemctl restart nginx"
echo "  Service status: sudo systemctl status gunicorn"
echo ""
