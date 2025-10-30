# 🎯 ULTRA-QUICK DEPLOYMENT GUIDE

**Time needed: 20 minutes**  
**Commands to run: 6**  
**Everything else: Automated!**

---

## ▶️ START HERE

### 1. Run Python Script (Windows PowerShell)

```powershell
cd "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\deployment"
python deploy_automated.py
```

Press ENTER when asked.

---

### 2. Upload Files (New PowerShell Window)

```powershell
cd "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\deployment"
scp "auto_deploy_server.sh" root@72.60.41.211:/root/auto_deploy_server.sh
```
Password: `Accresystem2023@`

```powershell
scp "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\firebase-service-account.json" root@72.60.41.211:/tmp/firebase-service-account.json
```
Password: `Accresystem2023@`

---

### 3. Connect to Server (PowerShell)

```powershell
ssh root@72.60.41.211
```
Password: `Accresystem2023@`

---

### 4. Run Deployment (On Server - Wait 15 minutes)

```bash
chmod +x /root/auto_deploy_server.sh && /root/auto_deploy_server.sh
```

☕ **Take a coffee break - this runs automatically!**

---

### 5. Move Firebase File (After deployment completes)

```bash
mv /tmp/firebase-service-account.json /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json && chown plpadmin:plpadmin /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json && chmod 600 /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json && supervisorctl restart plp_accreditation
```

---

### 6. Install SSL (Final Step)

```bash
apt-get install -y certbot python3-certbot-nginx && certbot --nginx -d plpaccreditation.com -d www.plpaccreditation.com --non-interactive --agree-tos --email admin@plpaccreditation.com && supervisorctl restart plp_accreditation && systemctl restart nginx
```

---

## ✅ DONE!

Visit: **https://plpaccreditation.com**

Login:
- Username: `admin`
- Password: `admin123`

---

## 🆘 Problems?

**Site not loading?**
```bash
supervisorctl restart plp_accreditation
systemctl restart nginx
```

**Check logs:**
```bash
tail -f /var/log/plp_accreditation.err.log
```

---

**That's it! Your system is now fully deployed with:**
✅ HTTPS  
✅ Firebase (same data)  
✅ Cloudinary (same storage)  
✅ Production-ready  

🎉 **Congratulations!**
