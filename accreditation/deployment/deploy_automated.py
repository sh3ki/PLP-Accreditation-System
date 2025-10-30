#!/usr/bin/env python3
"""
PLP Accreditation System - Automated Deployment Script
This script will fully deploy your Django application to the VPS server.

Server: 72.60.41.211
Domain: plpaccreditation.com
"""

import os
import sys
import subprocess
import time
import json

# Configuration from user
CONFIG = {
    'vps_ip': '72.60.41.211',
    'vps_password': 'Accresystem2023@',
    'domain': 'plpaccreditation.com',
    'domain_www': 'www.plpaccreditation.com',
    'postgres_password': '123',
    'django_admin_user': 'admin',
    'django_admin_password': 'admin123',
    'django_admin_email': 'admin@plpaccreditation.com',
    'cloudinary_api_key': '489778494632171',
    'cloudinary_api_secret': '-s7N1lsC1JoshfVmlCubvJJU0T8',
    'cloudinary_cloud_name': 'dygrh6ztt',
    'email_user': 'accreditationsystem2023@gmail.com',
    'email_password': 'tjgh wibm ddtg eqml',
    'github_repo': 'https://github.com/sh3ki/PLP-Accreditation-System.git',
    'project_path': '/home/plpadmin/PLP-Accreditation-System/accreditation',
    'user': 'plpadmin',
    'user_password': 'PLPAdmin2023@',
}

def print_step(step_num, total_steps, message):
    """Print formatted step message"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}/{total_steps}: {message}")
    print(f"{'='*80}\n")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ ERROR: {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def generate_secret_key():
    """Generate Django secret key"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for i in range(50))

def create_deployment_script():
    """Create the main deployment script that will run on the server"""
    
    secret_key = generate_secret_key()
    
    # Escape special characters in credentials
    cloudinary_secret = CONFIG['cloudinary_api_secret'].replace("'", "'\"'\"'")
    postgres_pass = CONFIG['postgres_password'].replace("'", "'\"'\"'")
    email_pass = CONFIG['email_password'].replace("'", "'\"'\"'")
    
    script = f'''#!/bin/bash
# PLP Accreditation System - Server Deployment Script
# This script runs on the VPS server

set -e  # Exit on any error

echo "============================================="
echo "PLP Accreditation System - Automated Deployment"
echo "============================================="
echo ""

# Color codes
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

print_step() {{
    echo -e "${{GREEN}}[$1/$2]${{NC}} $3"
}}

print_error() {{
    echo -e "${{RED}}ERROR: $1${{NC}}"
}}

print_success() {{
    echo -e "${{GREEN}}✓ $1${{NC}}"
}}

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
if id "{CONFIG['user']}" &>/dev/null; then
    print_success "User {CONFIG['user']} already exists"
else
    useradd -m -s /bin/bash {CONFIG['user']}
    echo "{CONFIG['user']}:{CONFIG['user_password']}" | chpasswd
    usermod -aG sudo {CONFIG['user']}
    print_success "User {CONFIG['user']} created"
fi

# Step 8: Setup PostgreSQL database
print_step 8 15 "Setting up PostgreSQL database..."
sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='plp_accreditation'" | grep -q 1 || \\
sudo -u postgres psql << EOF
CREATE DATABASE plp_accreditation;
CREATE USER plpuser WITH PASSWORD '{postgres_pass}';
ALTER ROLE plpuser SET client_encoding TO 'utf8';
ALTER ROLE plpuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE plpuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE plp_accreditation TO plpuser;
\\q
EOF
print_success "Database configured"

# Step 9: Clone repository as plpadmin user
print_step 9 15 "Cloning application repository..."
cd /home/{CONFIG['user']}
if [ -d "PLP-Accreditation-System" ]; then
    print_success "Repository already exists, pulling latest changes..."
    cd PLP-Accreditation-System
    sudo -u {CONFIG['user']} git pull origin master
else
    sudo -u {CONFIG['user']} git clone {CONFIG['github_repo']}
    print_success "Repository cloned"
fi

# Step 10: Setup Python virtual environment
print_step 10 15 "Setting up Python virtual environment..."
cd /home/{CONFIG['user']}/PLP-Accreditation-System/accreditation
if [ ! -d "venv" ]; then
    sudo -u {CONFIG['user']} python3 -m venv venv
fi
sudo -u {CONFIG['user']} bash << 'USEREOF'
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
USEREOF
print_success "Virtual environment configured"

# Step 11: Create .env file
print_step 11 15 "Creating environment configuration..."
cat > /home/{CONFIG['user']}/PLP-Accreditation-System/accreditation/.env << 'ENVEOF'
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS={CONFIG['domain']},{CONFIG['domain_www']},{CONFIG['vps_ip']}

DB_ENGINE=django.db.backends.postgresql
DB_NAME=plp_accreditation
DB_USER=plpuser
DB_PASSWORD={postgres_pass}
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER={CONFIG['email_user']}
EMAIL_HOST_PASSWORD={email_pass}

CLOUDINARY_API_KEY={CONFIG['cloudinary_api_key']}
CLOUDINARY_API_SECRET={cloudinary_secret}
ENVEOF
chown {CONFIG['user']}:{CONFIG['user']} /home/{CONFIG['user']}/PLP-Accreditation-System/accreditation/.env
chmod 600 /home/{CONFIG['user']}/PLP-Accreditation-System/accreditation/.env
print_success "Environment file created"

# Step 12: Run Django migrations and setup
print_step 12 15 "Setting up Django application..."
cd /home/{CONFIG['user']}/PLP-Accreditation-System/accreditation
sudo -u {CONFIG['user']} bash << 'DJANGOEOF'
source venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='{CONFIG['django_admin_user']}').exists() or User.objects.create_superuser('{CONFIG['django_admin_user']}', '{CONFIG['django_admin_email']}', '{CONFIG['django_admin_password']}')" | python manage.py shell
DJANGOEOF
print_success "Django application configured"

# Step 13: Set proper permissions
print_step 13 15 "Setting file permissions..."
chown -R {CONFIG['user']}:www-data /home/{CONFIG['user']}/PLP-Accreditation-System
chmod -R 755 /home/{CONFIG['user']}/PLP-Accreditation-System
print_success "Permissions set"

# Step 14: Configure Supervisor (Gunicorn)
print_step 14 15 "Configuring application server..."
cat > /etc/supervisor/conf.d/plp_accreditation.conf << 'SUPEOF'
[program:plp_accreditation]
directory=/home/{CONFIG['user']}/PLP-Accreditation-System/accreditation
command=/home/{CONFIG['user']}/PLP-Accreditation-System/accreditation/venv/bin/gunicorn --workers 3 --bind unix:/home/{CONFIG['user']}/PLP-Accreditation-System/accreditation/gunicorn.sock accreditation.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/plp_accreditation.err.log
stdout_logfile=/var/log/plp_accreditation.out.log
user={CONFIG['user']}
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
server {{
    listen 80;
    server_name {CONFIG['domain']} {CONFIG['domain_www']};
    
    client_max_body_size 50M;
    
    location = /favicon.ico {{ access_log off; log_not_found off; }}
    
    location /static/ {{
        alias /home/{CONFIG['user']}/PLP-Accreditation-System/accreditation/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
    
    location /media/ {{
        alias /home/{CONFIG['user']}/PLP-Accreditation-System/accreditation/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
    
    location / {{
        include proxy_params;
        proxy_pass http://unix:/home/{CONFIG['user']}/PLP-Accreditation-System/accreditation/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
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
echo "  HTTP:  http://{CONFIG['domain']}"
echo "  HTTP:  http://{CONFIG['vps_ip']}"
echo ""
echo "Next step: Install SSL certificate"
echo "Run this command to enable HTTPS:"
echo ""
echo "  apt-get install -y certbot python3-certbot-nginx"
echo "  certbot --nginx -d {CONFIG['domain']} -d {CONFIG['domain_www']} --non-interactive --agree-tos --email {CONFIG['django_admin_email']}"
echo ""
echo "Admin Panel: https://{CONFIG['domain']}/admin/"
echo "Username: {CONFIG['django_admin_user']}"
echo "Password: {CONFIG['django_admin_password']}"
echo ""
echo "To view logs:"
echo "  sudo tail -f /var/log/plp_accreditation.err.log"
echo ""
echo "To restart application:"
echo "  sudo supervisorctl restart plp_accreditation"
echo ""
'''
    
    return script

def main():
    """Main deployment function"""
    
    print("\n" + "="*80)
    print("🚀 PLP ACCREDITATION SYSTEM - AUTOMATED DEPLOYMENT")
    print("="*80)
    print(f"\nTarget Server: {CONFIG['vps_ip']}")
    print(f"Domain: {CONFIG['domain']}")
    print(f"GitHub: {CONFIG['github_repo']}")
    print("\n" + "="*80 + "\n")
    
    # Step 1: Create deployment script
    print_step(1, 4, "Creating deployment script...")
    deployment_script = create_deployment_script()
    
    # Save to file
    script_path = "auto_deploy_server.sh"
    with open(script_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(deployment_script)
    print_success(f"Deployment script created: {script_path}")
    
    # Step 2: Prepare Firebase service account file
    print_step(2, 4, "Checking Firebase service account file...")
    firebase_json_path = r"C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\firebase-service-account.json"
    
    if not os.path.exists(firebase_json_path):
        print_error(f"Firebase service account file not found at: {firebase_json_path}")
        sys.exit(1)
    print_success("Firebase service account file found")
    
    # Step 3: Display connection information
    print_step(3, 4, "Preparing to connect to server...")
    print_info("You will need to enter the root password when prompted")
    print_info(f"Password: {CONFIG['vps_password']}")
    print_info("\nThe script will:")
    print_info("  1. Upload deployment script to server")
    print_info("  2. Upload Firebase credentials to server")
    print_info("  3. Run automated deployment")
    print_info("  4. Install SSL certificate")
    print_info("\nThis will take approximately 10-15 minutes.")
    
    input("\n📌 Press ENTER to start deployment...")
    
    # Step 4: Generate and display commands
    print_step(4, 4, "Deployment Commands")
    
    print("\n" + "="*80)
    print("PLEASE RUN THESE COMMANDS IN ORDER:")
    print("="*80 + "\n")
    
    print("1️⃣  CONNECT TO SERVER:")
    print(f"   ssh root@{CONFIG['vps_ip']}")
    print(f"   Password: {CONFIG['vps_password']}\n")
    
    print("2️⃣  UPLOAD DEPLOYMENT SCRIPT (from your local machine in a new terminal):")
    print(f'   scp "{script_path}" root@{CONFIG["vps_ip"]}:/root/auto_deploy_server.sh\n')
    
    print("3️⃣  UPLOAD FIREBASE CREDENTIALS (from your local machine):")
    print(f'   scp "{firebase_json_path}" root@{CONFIG["vps_ip"]}:/tmp/firebase-service-account.json\n')
    
    print("4️⃣  ON THE SERVER, RUN THE DEPLOYMENT SCRIPT:")
    print("   chmod +x /root/auto_deploy_server.sh")
    print("   /root/auto_deploy_server.sh\n")
    
    print("5️⃣  MOVE FIREBASE FILE TO PROJECT (after deployment completes):")
    print(f"   mv /tmp/firebase-service-account.json {CONFIG['project_path']}/firebase-service-account.json")
    print(f"   chown {CONFIG['user']}:{CONFIG['user']} {CONFIG['project_path']}/firebase-service-account.json")
    print(f"   chmod 600 {CONFIG['project_path']}/firebase-service-account.json")
    print("   supervisorctl restart plp_accreditation\n")
    
    print("6️⃣  INSTALL SSL CERTIFICATE (final step):")
    print("   apt-get install -y certbot python3-certbot-nginx")
    print(f"   certbot --nginx -d {CONFIG['domain']} -d {CONFIG['domain_www']} --non-interactive --agree-tos --email {CONFIG['django_admin_email']}")
    print("   supervisorctl restart plp_accreditation")
    print("   systemctl restart nginx\n")
    
    print("="*80)
    print("✅ AFTER COMPLETION, YOUR SITE WILL BE LIVE AT:")
    print("="*80)
    print(f"   🌐 https://{CONFIG['domain']}")
    print(f"   👤 Admin: https://{CONFIG['domain']}/admin/")
    print(f"   📧 Username: {CONFIG['django_admin_user']}")
    print(f"   🔑 Password: {CONFIG['django_admin_password']}")
    print("="*80 + "\n")
    
    print_success("Deployment script ready!")
    print_info(f"Script saved to: {os.path.abspath(script_path)}")
    print_info("\nFollow the commands above to complete deployment.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Deployment failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
