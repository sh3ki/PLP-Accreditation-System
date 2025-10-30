#!/bin/bash
# PLP Accreditation System - Server Deployment Script
# This script runs on the VPS server

set -e  # Exit on any error

echo "============================================="
echo "PLP Accreditation System - Automated Deployment"
echo "============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}[$1/$2]${NC} $3"
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Step 1: Update system
print_step 1 15 "Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
print_success "System updated"

# Step 2: Install Python and dependencies
print_step 2 15 "Installing Python and build tools..."
apt-get install -y -qq python3 python3-pip python3-venv python3-dev build-essential libssl-dev libffi-dev
print_success "Python installed"

# Step 3: Install Nginx
print_step 3 15 "Installing Nginx web server..."
apt-get install -y -qq nginx
systemctl start nginx
systemctl enable nginx
print_success "Nginx installed and started"

# Step 4: Install PostgreSQL
print_step 4 15 "Installing PostgreSQL database..."
apt-get install -y -qq postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql
print_success "PostgreSQL installed and started"

# Step 5: Install Supervisor and Git
print_step 5 15 "Installing Supervisor and Git..."
apt-get install -y -qq supervisor git
systemctl start supervisor
systemctl enable supervisor
print_success "Supervisor and Git installed"

# Step 6: Configure firewall
print_step 6 15 "Configuring firewall..."
apt-get install -y -qq ufw
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
print_success "Firewall configured"

# Step 7: Create non-root user
print_step 7 15 "Creating application user..."
if id "plpadmin" &>/dev/null; then
    print_success "User plpadmin already exists"
else
    useradd -m -s /bin/bash plpadmin
    echo "plpadmin:PLPAdmin2023@" | chpasswd
    usermod -aG sudo plpadmin
    print_success "User plpadmin created"
fi

# Step 8: Setup PostgreSQL database
print_step 8 15 "Setting up PostgreSQL database..."
sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='plp_accreditation'" | grep -q 1 || \
sudo -u postgres psql << EOF
CREATE DATABASE plp_accreditation;
CREATE USER plpuser WITH PASSWORD '123';
ALTER ROLE plpuser SET client_encoding TO 'utf8';
ALTER ROLE plpuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE plpuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE plp_accreditation TO plpuser;
\q
EOF
print_success "Database configured"

# Step 9: Clone repository as plpadmin user
print_step 9 15 "Cloning application repository..."
cd /home/plpadmin
if [ -d "PLP-Accreditation-System" ]; then
    print_success "Repository already exists, pulling latest changes..."
    cd PLP-Accreditation-System
    sudo -u plpadmin git pull origin master
else
    sudo -u plpadmin git clone https://github.com/sh3ki/PLP-Accreditation-System.git
    print_success "Repository cloned"
fi

# Step 10: Setup Python virtual environment
print_step 10 15 "Setting up Python virtual environment..."
cd /home/plpadmin/PLP-Accreditation-System/accreditation
if [ ! -d "venv" ]; then
    sudo -u plpadmin python3 -m venv venv
fi
sudo -u plpadmin bash << 'USEREOF'
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
USEREOF
print_success "Virtual environment configured"

# Step 11: Create .env file
print_step 11 15 "Creating environment configuration..."
cat > /home/plpadmin/PLP-Accreditation-System/accreditation/.env << 'ENVEOF'
SECRET_KEY=vr-%6$kRpNEpblF1bTVWPdsT99B_b6Knsud$Jv+zGlY8a@oT()
DEBUG=False
ALLOWED_HOSTS=plpaccreditation.com,www.plpaccreditation.com,72.60.41.211

DB_ENGINE=django.db.backends.postgresql
DB_NAME=plp_accreditation
DB_USER=plpuser
DB_PASSWORD=123
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=accreditationsystem2023@gmail.com
EMAIL_HOST_PASSWORD=tjgh wibm ddtg eqml

CLOUDINARY_API_KEY=489778494632171
CLOUDINARY_API_SECRET=-s7N1lsC1JoshfVmlCubvJJU0T8
ENVEOF
chown plpadmin:plpadmin /home/plpadmin/PLP-Accreditation-System/accreditation/.env
chmod 600 /home/plpadmin/PLP-Accreditation-System/accreditation/.env
print_success "Environment file created"

# Step 12: Run Django migrations and setup
print_step 12 15 "Setting up Django application..."
cd /home/plpadmin/PLP-Accreditation-System/accreditation
sudo -u plpadmin bash << 'DJANGOEOF'
source venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@plpaccreditation.com', 'admin123')" | python manage.py shell
DJANGOEOF
print_success "Django application configured"

# Step 13: Set proper permissions
print_step 13 15 "Setting file permissions..."
chown -R plpadmin:www-data /home/plpadmin/PLP-Accreditation-System
chmod -R 755 /home/plpadmin/PLP-Accreditation-System
print_success "Permissions set"

# Step 14: Configure Supervisor (Gunicorn)
print_step 14 15 "Configuring application server..."
cat > /etc/supervisor/conf.d/plp_accreditation.conf << 'SUPEOF'
[program:plp_accreditation]
directory=/home/plpadmin/PLP-Accreditation-System/accreditation
command=/home/plpadmin/PLP-Accreditation-System/accreditation/venv/bin/gunicorn --workers 3 --bind unix:/home/plpadmin/PLP-Accreditation-System/accreditation/gunicorn.sock accreditation.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/plp_accreditation.err.log
stdout_logfile=/var/log/plp_accreditation.out.log
user=plpadmin
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8

[group:plp_group]
programs=plp_accreditation
SUPEOF
supervisorctl reread
supervisorctl update
supervisorctl start plp_accreditation
sleep 5
print_success "Application server configured"

# Step 15: Configure Nginx
print_step 15 15 "Configuring web server..."
cat > /etc/nginx/sites-available/plp_accreditation << 'NGINXEOF'
server {
    listen 80;
    server_name plpaccreditation.com www.plpaccreditation.com;
    
    client_max_body_size 50M;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/plpadmin/PLP-Accreditation-System/accreditation/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/plpadmin/PLP-Accreditation-System/accreditation/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/plpadmin/PLP-Accreditation-System/accreditation/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/plp_accreditation /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
print_success "Web server configured"

echo ""
echo "============================================="
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "============================================="
echo ""
echo "Your application is now running at:"
echo "  HTTP:  http://plpaccreditation.com"
echo "  HTTP:  http://72.60.41.211"
echo ""
echo "Next step: Install SSL certificate"
echo "Run this command to enable HTTPS:"
echo ""
echo "  apt-get install -y certbot python3-certbot-nginx"
echo "  certbot --nginx -d plpaccreditation.com -d www.plpaccreditation.com --non-interactive --agree-tos --email admin@plpaccreditation.com"
echo ""
echo "Admin Panel: https://plpaccreditation.com/admin/"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "To view logs:"
echo "  sudo tail -f /var/log/plp_accreditation.err.log"
echo ""
echo "To restart application:"
echo "  sudo supervisorctl restart plp_accreditation"
echo ""
