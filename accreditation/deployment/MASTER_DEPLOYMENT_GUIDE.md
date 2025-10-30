# 🚀 COMPLETE DEPLOYMENT GUIDE: PLP Accreditation System to Hostinger KVM1

## 📌 Overview
This guide will walk you through deploying your Django PLP Accreditation System to Hostinger's KVM1 VPS with your domain **plpaccreditation.com**.

**Estimated Time**: 2-3 hours for first-time deployment

---

## 📋 Prerequisites

✅ **What You Have**:
- Hostinger KVM1 VPS (active)
- Domain: plpaccreditation.com (registered on Hostinger)
- GitHub Repository: https://github.com/sh3ki/PLP-Accreditation-System
- Firebase service account JSON file
- Gmail app password for OTP emails

✅ **What You Need**:
- VPS IP Address (get from Hostinger hPanel)
- VPS root password (check email or reset in hPanel)
- SSH client (PowerShell on Windows, built-in on Mac/Linux)
- 2-3 hours of focused time

---

## 🎯 PHASE 1: INITIAL VPS SETUP (30 minutes)

### Step 1.1: Get VPS Access Details

1. Login to **Hostinger hPanel**: https://hpanel.hostinger.com
2. Click **VPS** in the left menu
3. Select your KVM1 VPS
4. Note down:
   - **IP Address**: (e.g., 123.45.67.89)
   - **SSH Port**: 22
   - **Root Password**: (reset if needed)

### Step 1.2: Connect to VPS

Open PowerShell and run:
```powershell
ssh root@YOUR_VPS_IP
```
*Replace YOUR_VPS_IP with your actual IP*

Type `yes` when prompted about authenticity, then enter your root password.

### Step 1.3: Update System

```bash
apt update
apt upgrade -y
```
Wait for updates to complete (5-10 minutes).

### Step 1.4: Create Non-Root User (Security)

```bash
adduser plpadmin
```
- Enter a strong password (write it down!)
- Press Enter for all other prompts

```bash
usermod -aG sudo plpadmin
```

### Step 1.5: Configure Firewall

```bash
apt install ufw -y
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```
Type `y` and press Enter when prompted.

Test: `ufw status` should show rules are active.

---

## 🎯 PHASE 2: INSTALL SOFTWARE (20 minutes)

### Step 2.1: Install Python

```bash
apt install python3 python3-pip python3-venv python3-dev build-essential libssl-dev libffi-dev -y
```

Verify: `python3 --version` should show Python 3.8 or higher.

### Step 2.2: Install Nginx

```bash
apt install nginx -y
systemctl start nginx
systemctl enable nginx
```

Test: Visit `http://YOUR_VPS_IP` in browser - should see Nginx welcome page.

### Step 2.3: Install PostgreSQL

```bash
apt install postgresql postgresql-contrib -y
systemctl start postgresql
systemctl enable postgresql
```

Verify: `sudo systemctl status postgresql` should show "active (running)".

### Step 2.4: Install Supervisor & Git

```bash
apt install supervisor git -y
systemctl start supervisor
systemctl enable supervisor
```

---

## 🎯 PHASE 3: CONFIGURE DOMAIN (15 minutes)

### Step 3.1: Update DNS Settings

1. Go to **Hostinger hPanel** → **Domains**
2. Click on **plpaccreditation.com**
3. Go to **DNS / Nameservers** → **DNS Records**
4. Add/Update these records:

   | Type | Name | Points to | TTL |
   |------|------|-----------|-----|
   | A | @ | YOUR_VPS_IP | 14400 |
   | A | www | YOUR_VPS_IP | 14400 |

5. Click **Add Record** for each

### Step 3.2: Wait for DNS Propagation

Usually takes 5-30 minutes. Check with:
```bash
ping plpaccreditation.com
```
Should show your VPS IP address.

---

## 🎯 PHASE 4: SETUP APPLICATION (20 minutes)

### Step 4.1: Switch to plpadmin User

```bash
su - plpadmin
```
Enter plpadmin password.

### Step 4.2: Clone Repository

```bash
cd /home/plpadmin
git clone https://github.com/sh3ki/PLP-Accreditation-System.git
cd PLP-Accreditation-System/accreditation
```

### Step 4.3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### Step 4.4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This takes 5-10 minutes. Wait for it to complete.

---

## 🎯 PHASE 5: CONFIGURE DATABASE (15 minutes)

### Step 5.1: Create PostgreSQL Database

```bash
sudo -u postgres psql
```

You're now in PostgreSQL shell. Run these commands one by one:

```sql
CREATE DATABASE plp_accreditation;
CREATE USER plpuser WITH PASSWORD 'YourStrongPassword123!';
ALTER ROLE plpuser SET client_encoding TO 'utf8';
ALTER ROLE plpuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE plpuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE plp_accreditation TO plpuser;
\q
```

**IMPORTANT**: Replace `YourStrongPassword123!` with your own strong password. **Write it down!**

---

## 🎯 PHASE 6: CONFIGURE ENVIRONMENT (20 minutes)

### Step 6.1: Generate Secret Key

On your **local Windows machine**, open PowerShell in your project directory:

```powershell
cd "c:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation"
python deployment\generate_secret_key.py
```

**Copy the SECRET_KEY** output.

### Step 6.2: Create .env File on Server

Back on your VPS (as plpadmin user):

```bash
cd /home/plpadmin/PLP-Accreditation-System/accreditation
nano .env
```

Paste this content (replace values with your actual data):

```env
SECRET_KEY=paste-your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=plpaccreditation.com,www.plpaccreditation.com,YOUR_VPS_IP

DB_ENGINE=django.db.backends.postgresql
DB_NAME=plp_accreditation
DB_USER=plpuser
DB_PASSWORD=YourStrongPassword123!
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=accreditationsystem2023@gmail.com
EMAIL_HOST_PASSWORD=tjgh wibm ddtg eqml

CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret
```

**Replace**:
- `paste-your-generated-secret-key-here` with the key you generated
- `YOUR_VPS_IP` with your actual VPS IP
- `YourStrongPassword123!` with your PostgreSQL password
- `your-cloudinary-api-key` with your actual Cloudinary API key
- `your-cloudinary-api-secret` with your actual Cloudinary API secret

**To get Cloudinary credentials**:
1. Go to https://cloudinary.com/console
2. Login to your account
3. Copy **API Key** and **API Secret** from the dashboard
4. Paste them into the .env file above

Save: Press `Ctrl+X`, then `Y`, then `Enter`.

### Step 6.3: Upload Firebase Service Account

On your local machine, you need to upload `firebase-service-account.json` to the server.

**Option A - Using SCP (from PowerShell):**
```powershell
scp "c:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\firebase-service-account.json" plpadmin@YOUR_VPS_IP:/home/plpadmin/PLP-Accreditation-System/accreditation/
```

**Option B - Manual Copy/Paste:**
On VPS:
```bash
nano /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json
```
Copy content from your local file and paste, then save.

---

## 🎯 PHASE 7: DJANGO SETUP (15 minutes)

### Step 7.1: Run Migrations

```bash
cd /home/plpadmin/PLP-Accreditation-System/accreditation
source venv/bin/activate
python manage.py migrate
```

### Step 7.2: Create Superuser

```bash
python manage.py createsuperuser
```

Enter username, email, and password. **Write these down!**

### Step 7.3: Collect Static Files

```bash
python manage.py collectstatic
```

Type `yes` when prompted.

### Step 7.4: Set Permissions

```bash
sudo chown -R plpadmin:www-data /home/plpadmin/PLP-Accreditation-System
sudo chmod -R 755 /home/plpadmin/PLP-Accreditation-System
```

---

## 🎯 PHASE 8: CONFIGURE GUNICORN & SUPERVISOR (15 minutes)

### Step 8.1: Test Gunicorn

```bash
cd /home/plpadmin/PLP-Accreditation-System/accreditation
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 accreditation.wsgi:application
```

Visit `http://YOUR_VPS_IP:8000` - should see your site (without CSS).

Press `Ctrl+C` to stop Gunicorn.

### Step 8.2: Configure Supervisor

```bash
sudo cp deployment/supervisor_plp_accreditation.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start plp_accreditation
```

Check status:
```bash
sudo supervisorctl status plp_accreditation
```

Should show "RUNNING".

---

## 🎯 PHASE 9: CONFIGURE NGINX (15 minutes)

### Step 9.1: Setup Nginx Configuration

```bash
sudo cp /home/plpadmin/PLP-Accreditation-System/accreditation/deployment/nginx_plp_accreditation /etc/nginx/sites-available/plp_accreditation

sudo ln -s /etc/nginx/sites-available/plp_accreditation /etc/nginx/sites-enabled/

sudo rm /etc/nginx/sites-enabled/default
```

### Step 9.2: Test & Restart Nginx

```bash
sudo nginx -t
```

Should say "syntax is ok" and "test is successful".

```bash
sudo systemctl restart nginx
```

### Step 9.3: Test HTTP Access

Visit `http://plpaccreditation.com` in your browser.

**Expected**: Site loads but browser shows "Not Secure" (we'll fix this next).

---

## 🎯 PHASE 10: INSTALL SSL CERTIFICATE (15 minutes)

### Step 10.1: Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Step 10.2: Obtain SSL Certificate

```bash
sudo certbot --nginx -d plpaccreditation.com -d www.plpaccreditation.com
```

When prompted:
1. Enter your email address
2. Type `Y` to agree to terms
3. Type `N` for sharing email (optional)

Certbot will automatically configure HTTPS!

### Step 10.3: Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

Should say "Congratulations, all simulated renewals succeeded".

---

## 🎯 PHASE 11: FINAL CONFIGURATION (10 minutes)

### Step 11.1: Update Settings for HTTPS

Since we now have SSL, we need to enable SSL redirects.

The settings.py file has already been updated to enable HTTPS security when DEBUG=False, so no changes needed!

### Step 11.2: Restart Services

```bash
sudo supervisorctl restart plp_accreditation
sudo systemctl restart nginx
```

---

## 🎯 PHASE 12: TESTING & VERIFICATION (15 minutes)

### ✅ Test Checklist

Visit https://plpaccreditation.com and verify:

- [ ] **HTTPS** - Padlock icon shows in browser
- [ ] **Login Page** - Loads correctly
- [ ] **Static Files** - CSS and images load
- [ ] **Login** - Can log in with superuser credentials
- [ ] **Dashboard** - Loads after login
- [ ] **Navigation** - All menu items work
- [ ] **Firebase** - Data loads from Firestore
- [ ] **File Upload** - Can upload documents
- [ ] **OTP Email** - Receives OTP emails (if configured)

### Check Logs

If anything doesn't work:

```bash
# Application logs
sudo tail -f /var/log/plp_accreditation.err.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

---

## 🎯 POST-DEPLOYMENT TASKS

### 1. Make Deploy Script Executable

```bash
chmod +x /home/plpadmin/PLP-Accreditation-System/accreditation/deployment/deploy.sh
```

### 2. Test Deployment Script

```bash
cd /home/plpadmin/PLP-Accreditation-System/accreditation/deployment
bash deploy.sh
```

### 3. Setup Automated Backups

Create backup script:
```bash
nano /home/plpadmin/backup_database.sh
```

Paste:
```bash
#!/bin/bash
BACKUP_DIR="/home/plpadmin/backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump plp_accreditation > $BACKUP_DIR/backup_$TIMESTAMP.sql
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

Make executable:
```bash
chmod +x /home/plpadmin/backup_database.sh
```

Add to crontab (daily at 2 AM):
```bash
crontab -e
```

Add this line:
```
0 2 * * * /home/plpadmin/backup_database.sh
```

---

## 📊 FUTURE UPDATES

When you push changes to GitHub and want to deploy:

1. **SSH into server**:
   ```bash
   ssh plpadmin@YOUR_VPS_IP
   ```

2. **Run deployment script**:
   ```bash
   cd /home/plpadmin/PLP-Accreditation-System/accreditation/deployment
   bash deploy.sh
   ```

That's it! The script handles pulling code, installing dependencies, collecting static files, running migrations, and restarting the application.

---

## 🆘 TROUBLESHOOTING

### Problem: 502 Bad Gateway

**Solution**:
```bash
sudo supervisorctl status plp_accreditation
sudo supervisorctl restart plp_accreditation
sudo tail -f /var/log/plp_accreditation.err.log
```

### Problem: Static Files Not Loading

**Solution**:
```bash
cd /home/plpadmin/PLP-Accreditation-System/accreditation
source venv/bin/activate
python manage.py collectstatic --clear
sudo systemctl restart nginx
```

### Problem: Database Connection Error

**Solution**:
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify .env file has correct DB password
3. Test connection: `sudo -u postgres psql -d plp_accreditation`

### Problem: Can't Access Admin Panel

**Solution**:
Visit `https://plpaccreditation.com/admin/` and login with superuser credentials.

---

## 📚 ADDITIONAL RESOURCES

- **Production Guide**: `deployment/PRODUCTION_GUIDE.md`
- **Deployment Checklist**: `deployment/DEPLOYMENT_CHECKLIST.md`
- **Command Reference**: `deployment/DEPLOYMENT_COMMANDS.md`

---

## 🎉 CONGRATULATIONS!

Your PLP Accreditation System is now live at:
### 🌐 https://plpaccreditation.com

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Initial Superuser**: _____________

---

## 📝 Important Security Notes

1. ✅ Never share your `.env` file
2. ✅ Keep database passwords secure
3. ✅ Regularly update system packages: `sudo apt update && sudo apt upgrade`
4. ✅ Monitor logs for suspicious activity
5. ✅ Backup database regularly
6. ✅ Keep Django and Python packages updated
7. ✅ Never set `DEBUG=True` in production

---

**Need Help?**
- Check logs: `/var/log/plp_accreditation.err.log`
- Review: `deployment/PRODUCTION_GUIDE.md`
- Hostinger Support: https://www.hostinger.com/contact
