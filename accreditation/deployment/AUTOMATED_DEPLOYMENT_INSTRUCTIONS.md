# 🚀 AUTOMATED DEPLOYMENT - QUICK START GUIDE

## ⚡ Deploy Your System in 3 Simple Steps

Your server: **72.60.41.211**  
Your domain: **plpaccreditation.com**  
All credentials: **Already configured in the script**

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### **STEP 1: Run the Python Script (On Your Windows Machine)**

Open PowerShell in this folder and run:

```powershell
cd "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\deployment"
python deploy_automated.py
```

This will:
- ✅ Create a deployment script with all your credentials
- ✅ Show you exactly what commands to run
- ✅ Generate all configuration files

---

### **STEP 2: Follow the Commands**

The script will show you 6 commands to run. Here's a preview:

#### 2.1 - Connect to Server
```powershell
ssh root@72.60.41.211
# Password: Accresystem2023@
```

#### 2.2 - Upload Deployment Script (NEW PowerShell window)
```powershell
scp "auto_deploy_server.sh" root@72.60.41.211:/root/auto_deploy_server.sh
```

#### 2.3 - Upload Firebase File (Same PowerShell window)
```powershell
scp "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\firebase-service-account.json" root@72.60.41.211:/tmp/firebase-service-account.json
```

#### 2.4 - Run Deployment (On the server in SSH)
```bash
chmod +x /root/auto_deploy_server.sh
/root/auto_deploy_server.sh
```

**⏱️ Wait 10-15 minutes** - The script will automatically:
- Install all software
- Setup database
- Clone your repo
- Configure everything
- Start your application

#### 2.5 - Move Firebase File (After deployment completes)
```bash
mv /tmp/firebase-service-account.json /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json
chown plpadmin:plpadmin /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json
chmod 600 /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json
supervisorctl restart plp_accreditation
```

#### 2.6 - Install SSL Certificate (Final step)
```bash
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d plpaccreditation.com -d www.plpaccreditation.com --non-interactive --agree-tos --email admin@plpaccreditation.com
supervisorctl restart plp_accreditation
systemctl restart nginx
```

---

### **STEP 3: Verify Deployment**

Visit: **https://plpaccreditation.com**

- ✅ Site should load with HTTPS (green padlock)
- ✅ Login works
- ✅ Dashboard loads
- ✅ Images load (Cloudinary working)
- ✅ Firebase data accessible

**Admin Panel**: https://plpaccreditation.com/admin/
- Username: `admin`
- Password: `admin123`

---

## 🎯 WHAT THE SCRIPT DOES AUTOMATICALLY

✅ Updates Ubuntu system  
✅ Installs Python, Nginx, PostgreSQL, Supervisor  
✅ Configures firewall  
✅ Creates database & user  
✅ Clones your GitHub repo  
✅ Sets up virtual environment  
✅ Installs all Python packages  
✅ Creates .env with ALL your credentials:
- Django SECRET_KEY (auto-generated)
- PostgreSQL password (123)
- Cloudinary API Key & Secret
- Email credentials
- All domains and IPs

✅ Runs Django migrations  
✅ Collects static files  
✅ Creates admin user (admin/admin123)  
✅ Configures Gunicorn  
✅ Configures Nginx  
✅ Starts application  

**YOU ONLY need to:**
1. Run commands shown by the script
2. Wait for completion
3. Install SSL certificate

---

## 📊 CREDENTIALS CONFIGURED

All these are **already in the deployment script**:

| Service | Credentials |
|---------|-------------|
| **VPS** | IP: 72.60.41.211<br>Root Password: Accresystem2023@ |
| **PostgreSQL** | Password: 123 |
| **Django Admin** | Username: admin<br>Password: admin123 |
| **Cloudinary** | API Key: 489778494632171<br>API Secret: -s7N1lsC1JoshfVmlCubvJJU0T8<br>Cloud: dygrh6ztt |
| **Email** | User: accreditationsystem2023@gmail.com<br>Password: tjgh wibm ddtg eqml |
| **Firebase** | File: firebase-service-account.json<br>(uploaded separately) |

---

## ⏱️ TIMELINE

- **Script generation**: 10 seconds
- **File upload**: 1 minute
- **Server deployment**: 10-15 minutes
- **SSL installation**: 2 minutes
- **TOTAL**: ~20 minutes

---

## 🆘 TROUBLESHOOTING

### If deployment script fails:

**Check logs:**
```bash
tail -f /var/log/plp_accreditation.err.log
```

**Restart application:**
```bash
supervisorctl restart plp_accreditation
```

**Restart Nginx:**
```bash
systemctl restart nginx
```

### If site doesn't load:

**Check status:**
```bash
supervisorctl status plp_accreditation
systemctl status nginx
```

**Verify DNS:**
```bash
ping plpaccreditation.com
# Should show: 72.60.41.211
```

---

## ✅ SUCCESS INDICATORS

After deployment, you should see:

```
✅ DEPLOYMENT COMPLETED SUCCESSFULLY!

Your application is now running at:
  HTTP:  http://plpaccreditation.com
  HTTP:  http://72.60.41.211

Next step: Install SSL certificate
```

Then after SSL installation:

- ✅ https://plpaccreditation.com (green padlock)
- ✅ Login page loads
- ✅ Can login as admin
- ✅ Dashboard shows
- ✅ Files can be uploaded
- ✅ Images display

---

## 🎉 THAT'S IT!

Your PLP Accreditation System will be **FULLY DEPLOYED** with:
- ✅ Same Firebase database
- ✅ Same Cloudinary storage
- ✅ Same email configuration
- ✅ Secure HTTPS
- ✅ Auto-restarts on failure
- ✅ Production-ready setup

**Total manual work: Copy/paste 6 commands. Everything else is automatic!**

---

**Need help?** Check the deployment logs or contact support.
