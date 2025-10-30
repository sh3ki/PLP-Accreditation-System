# ⚡ Quick Reference - PLP Accreditation System Deployment

## 🎯 One-Page Overview

### Your Setup
- **Local**: Windows development machine
- **Server**: Hostinger KVM1 VPS
- **Domain**: plpaccreditation.com
- **GitHub**: sh3ki/PLP-Accreditation-System
- **Production URL**: https://plpaccreditation.com

---

## 📝 Pre-Deployment Checklist

```
☐ VPS IP Address: _______________
☐ VPS Root Password: _______________
☐ PostgreSQL Password (choose): _______________
☐ Django Admin Username: _______________
☐ Django Admin Password: _______________
☐ Cloudinary API Key: _______________
☐ Cloudinary API Secret: _______________
```

---

## 🚀 Deployment in 30 Commands

### On Your VPS (via SSH):

```bash
# 1. UPDATE SYSTEM
apt update && apt upgrade -y

# 2. CREATE USER
adduser plpadmin
usermod -aG sudo plpadmin

# 3. SETUP FIREWALL
apt install ufw -y
ufw allow OpenSSH && ufw allow 80/tcp && ufw allow 443/tcp
ufw enable

# 4. INSTALL SOFTWARE
apt install python3 python3-pip python3-venv python3-dev build-essential -y
apt install nginx postgresql postgresql-contrib supervisor git -y

# 5. CONFIGURE DNS (in Hostinger hPanel)
# Add A records: @ → VPS_IP and www → VPS_IP

# 6. SWITCH USER & CLONE
su - plpadmin
cd /home/plpadmin
git clone https://github.com/sh3ki/PLP-Accreditation-System.git
cd PLP-Accreditation-System/accreditation

# 7. PYTHON ENVIRONMENT
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 8. CREATE DATABASE
sudo -u postgres psql
# In PostgreSQL:
CREATE DATABASE plp_accreditation;
CREATE USER plpuser WITH PASSWORD 'YourPassword';
ALTER ROLE plpuser SET client_encoding TO 'utf8';
ALTER ROLE plpuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE plpuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE plp_accreditation TO plpuser;
\q

# 9. CREATE .ENV FILE
nano .env
# Paste configuration (see .env template below)

# 10. UPLOAD FIREBASE JSON
# Use SCP from local machine or nano to paste content

# 11. DJANGO SETUP
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# 12. PERMISSIONS
sudo chown -R plpadmin:www-data /home/plpadmin/PLP-Accreditation-System
sudo chmod -R 755 /home/plpadmin/PLP-Accreditation-System

# 13. CONFIGURE SUPERVISOR
sudo cp deployment/supervisor_plp_accreditation.conf /etc/supervisor/conf.d/
sudo supervisorctl reread && sudo supervisorctl update
sudo supervisorctl start plp_accreditation

# 14. CONFIGURE NGINX
sudo cp deployment/nginx_plp_accreditation /etc/nginx/sites-available/plp_accreditation
sudo ln -s /etc/nginx/sites-available/plp_accreditation /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 15. INSTALL SSL
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d plpaccreditation.com -d www.plpaccreditation.com

# 16. RESTART SERVICES
sudo supervisorctl restart plp_accreditation
sudo systemctl restart nginx

# ✅ DONE! Visit https://plpaccreditation.com
```

---

## 📄 .env File Template

```env
SECRET_KEY=generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=plpaccreditation.com,www.plpaccreditation.com,VPS_IP

DB_ENGINE=django.db.backends.postgresql
DB_NAME=plp_accreditation
DB_USER=plpuser
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=accreditationsystem2023@gmail.com
EMAIL_HOST_PASSWORD=tjgh wibm ddtg eqml

CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## 🔧 Essential Commands

### Service Management
```bash
# Check status
sudo supervisorctl status plp_accreditation

# Restart application
sudo supervisorctl restart plp_accreditation

# View logs
sudo tail -f /var/log/plp_accreditation.err.log
```

### Nginx
```bash
# Test config
sudo nginx -t

# Restart
sudo systemctl restart nginx

# View logs
sudo tail -f /var/log/nginx/error.log
```

### Database Backup
```bash
sudo -u postgres pg_dump plp_accreditation > backup.sql
```

### Deploy Updates
```bash
cd /home/plpadmin/PLP-Accreditation-System/accreditation/deployment
bash deploy.sh
```

---

## 🆘 Emergency Commands

### Application won't start:
```bash
sudo supervisorctl status
sudo tail -f /var/log/plp_accreditation.err.log
sudo supervisorctl restart plp_accreditation
```

### 502 Bad Gateway:
```bash
sudo supervisorctl restart plp_accreditation
sudo systemctl restart nginx
```

### Static files missing:
```bash
cd /home/plpadmin/PLP-Accreditation-System/accreditation
source venv/bin/activate
python manage.py collectstatic --clear
sudo systemctl restart nginx
```

---

## 📊 Ports Used
- **80**: HTTP (redirects to HTTPS)
- **443**: HTTPS (production traffic)
- **22**: SSH (server access)
- **5432**: PostgreSQL (localhost only)

---

## 🔗 Important URLs

- **Production Site**: https://plpaccreditation.com
- **Admin Panel**: https://plpaccreditation.com/admin/
- **Hostinger hPanel**: https://hpanel.hostinger.com
- **Firebase Console**: https://console.firebase.google.com
- **Cloudinary Console**: https://cloudinary.com/console
- **GitHub Repo**: https://github.com/sh3ki/PLP-Accreditation-System

---

## 📞 Support Resources

| Issue | Resource |
|-------|----------|
| Detailed steps | MASTER_DEPLOYMENT_GUIDE.md |
| Credentials help | CREDENTIALS_GUIDE.md |
| Server management | PRODUCTION_GUIDE.md |
| VPS issues | Hostinger Support |
| Application errors | Check logs |

---

## ✅ Post-Deployment Verification

```bash
# 1. Check Supervisor
sudo supervisorctl status plp_accreditation
# Should show: RUNNING

# 2. Check Nginx
sudo systemctl status nginx
# Should show: active (running)

# 3. Check PostgreSQL
sudo systemctl status postgresql
# Should show: active (running)

# 4. Check SSL
sudo certbot certificates
# Should show certificates for both domains

# 5. Test site
curl https://plpaccreditation.com
# Should return HTML

# 6. Test admin
# Visit: https://plpaccreditation.com/admin/
```

---

## 🎯 Success Indicators

✅ Site loads at https://plpaccreditation.com  
✅ Green padlock (SSL) in browser  
✅ Can login with credentials  
✅ Dashboard loads  
✅ Can upload files  
✅ Images display  
✅ OTP emails arrive  

---

**Need more details?** See `MASTER_DEPLOYMENT_GUIDE.md`
