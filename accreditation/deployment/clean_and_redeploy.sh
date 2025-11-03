#!/bin/bash

# Clean and Redeploy Script for PLP Accreditation System
# This script removes all deployed files and redeploys from scratch

set -e  # Exit on error

echo "============================================"
echo "  PLP Accreditation System - Clean Redeploy"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="plp-accreditation"
APP_DIR="/home/plpadmin/PLP-Accreditation-System"
VENV_DIR="$APP_DIR/accreditation/venv"
NGINX_CONF="/etc/nginx/sites-available/plp_accreditation"
GUNICORN_SERVICE="/etc/systemd/system/gunicorn.service"

echo -e "${YELLOW}Step 1: Stopping services...${NC}"
sudo systemctl stop gunicorn 2>/dev/null || echo "Gunicorn service not running"
sudo systemctl stop nginx 2>/dev/null || echo "Nginx not running"
echo -e "${GREEN}✓ Services stopped${NC}"
echo ""

echo -e "${YELLOW}Step 2: Removing application directory...${NC}"
if [ -d "$APP_DIR" ]; then
    sudo rm -rf "$APP_DIR"
    echo -e "${GREEN}✓ Application directory removed${NC}"
else
    echo "Application directory does not exist"
fi
echo ""

echo -e "${YELLOW}Step 3: Removing systemd service file...${NC}"
if [ -f "$GUNICORN_SERVICE" ]; then
    sudo rm -f "$GUNICORN_SERVICE"
    echo -e "${GREEN}✓ Gunicorn service file removed${NC}"
else
    echo "Service file does not exist"
fi
echo ""

echo -e "${YELLOW}Step 4: Removing nginx configuration...${NC}"
if [ -f "$NGINX_CONF" ]; then
    sudo rm -f "$NGINX_CONF"
    sudo rm -f "/etc/nginx/sites-enabled/plp_accreditation" 2>/dev/null || true
    echo -e "${GREEN}✓ Nginx configuration removed${NC}"
else
    echo "Nginx configuration does not exist"
fi
echo ""

echo -e "${YELLOW}Step 5: Removing log files...${NC}"
sudo rm -f /var/log/plp_accreditation.*.log 2>/dev/null || true
echo -e "${GREEN}✓ Log files removed${NC}"
echo ""

echo -e "${YELLOW}Step 6: Reloading systemd daemon...${NC}"
sudo systemctl daemon-reload
echo -e "${GREEN}✓ Systemd daemon reloaded${NC}"
echo ""

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Clean-up completed successfully!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Clone the repository to $APP_DIR"
echo "2. Set up virtual environment"
echo "3. Install dependencies"
echo "4. Configure environment variables"
echo "5. Set up gunicorn service"
echo "6. Configure nginx"
echo "7. Start services"
echo ""
echo -e "${YELLOW}Run the deployment script to continue.${NC}"
