# ✅ AUTOMATED DEPLOYMENT CHECKLIST

**Copy/paste these commands in order. Check each box when done.**

---

## 🖥️ ON YOUR WINDOWS MACHINE

### [ ] 1. Generate Deployment Script

Open PowerShell in the deployment folder:

```powershell
cd "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\deployment"
python deploy_automated.py
```

**Expected output:** Script creates `auto_deploy_server.sh` and shows instructions

---

## 📤 UPLOAD FILES TO SERVER

### [ ] 2. Upload Deployment Script

**Open a NEW PowerShell window** (keep the first one for SSH):

```powershell
cd "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\deployment"
scp "auto_deploy_server.sh" root@72.60.41.211:/root/auto_deploy_server.sh
```

**Password when prompted:** `Accresystem2023@`

---

### [ ] 3. Upload Firebase Credentials

**Same PowerShell window:**

```powershell
scp "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\firebase-service-account.json" root@72.60.41.211:/tmp/firebase-service-account.json
```

**Password when prompted:** `Accresystem2023@`

---

## 🔗 CONNECT TO SERVER

### [ ] 4. SSH to Server

**In your first PowerShell window (or a new one):**

```powershell
ssh root@72.60.41.211
```

**Password:** `Accresystem2023@`

Type `yes` if asked about fingerprint.

---

## 🚀 RUN DEPLOYMENT (ON SERVER)

### [ ] 5. Make Script Executable

```bash
chmod +x /root/auto_deploy_server.sh
```

---

### [ ] 6. Run Deployment Script

```bash
/root/auto_deploy_server.sh
```

**⏱️ WAIT 10-15 MINUTES**

You'll see steps 1-15 being executed automatically.

**Expected final message:**
```
✅ DEPLOYMENT COMPLETED SUCCESSFULLY!
```

---

### [ ] 7. Move Firebase File to Project

```bash
mv /tmp/firebase-service-account.json /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json
chown plpadmin:plpadmin /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json
chmod 600 /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json
supervisorctl restart plp_accreditation
```

---

### [ ] 8. Test HTTP Access

**Open browser and visit:** `http://plpaccreditation.com`

**Should see:** Your login page (without HTTPS yet)

---

## 🔒 INSTALL SSL CERTIFICATE

### [ ] 9. Install Certbot

```bash
apt-get install -y certbot python3-certbot-nginx
```

---

### [ ] 10. Get SSL Certificate

```bash
certbot --nginx -d plpaccreditation.com -d www.plpaccreditation.com --non-interactive --agree-tos --email admin@plpaccreditation.com
```

**Wait 1-2 minutes...**

**Expected output:** `Successfully received certificate`

---

### [ ] 11. Restart Services

```bash
supervisorctl restart plp_accreditation
systemctl restart nginx
```

---

## ✅ VERIFY DEPLOYMENT

### [ ] 12. Test HTTPS

**Visit:** `https://plpaccreditation.com`

**Should see:**
- ✅ Green padlock (HTTPS)
- ✅ Login page loads
- ✅ CSS styles applied
- ✅ Images visible

---

### [ ] 13. Test Login

**Login with:**
- Username: `admin`
- Password: `admin123`

**Should:**
- ✅ Login successful
- ✅ Redirect to dashboard
- ✅ Dashboard loads completely

---

### [ ] 14. Test Admin Panel

**Visit:** `https://plpaccreditation.com/admin/`

**Login with same credentials**

**Should see:** Django admin interface

---

### [ ] 15. Test File Upload

**Try uploading a document or image**

**Should:**
- ✅ Upload succeeds
- ✅ File appears in system
- ✅ Image displays (Cloudinary working)

---

### [ ] 16. Check Firebase Data

**Navigate through the system**

**Should:**
- ✅ User data loads
- ✅ Department data visible
- ✅ All Firestore data accessible

---

## 🎉 DEPLOYMENT COMPLETE!

### Your site is now live at:
- 🌐 **https://plpaccreditation.com**
- 👤 **Admin:** https://plpaccreditation.com/admin/
- 📧 **Username:** admin
- 🔑 **Password:** admin123

---

## 📊 POST-DEPLOYMENT

### [ ] 17. Save Important Info

Write down:
- ✅ VPS IP: 72.60.41.211
- ✅ Admin username: admin
- ✅ Admin password: admin123
- ✅ PostgreSQL password: 123

---

### [ ] 18. Check Logs (Optional)

```bash
# Application logs
tail -f /var/log/plp_accreditation.err.log

# Nginx logs
tail -f /var/log/nginx/error.log
```

Press `Ctrl+C` to exit log view

---

### [ ] 19. Setup Daily Backups (Optional)

```bash
# Create backup script
cat > /home/plpadmin/backup_database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/plpadmin/backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump plp_accreditation > $BACKUP_DIR/backup_$TIMESTAMP.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /home/plpadmin/backup_database.sh

# Schedule daily at 2 AM
crontab -e
# Add this line:
0 2 * * * /home/plpadmin/backup_database.sh
```

---

## 🔄 FUTURE UPDATES

When you push changes to GitHub:

```bash
ssh plpadmin@72.60.41.211
# Password: PLPAdmin2023@

cd /home/plpadmin/PLP-Accreditation-System/accreditation
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart plp_accreditation
```

---

## ✅ ALL DONE!

**Total time:** ~20 minutes  
**Manual commands:** 6 (copy/paste)  
**Everything else:** Fully automated!

Your PLP Accreditation System is now:
- ✅ Live and secure (HTTPS)
- ✅ Using same Firebase data
- ✅ Using same Cloudinary storage
- ✅ Production-ready
- ✅ Auto-restarts on failure

**Congratulations! 🎉**
