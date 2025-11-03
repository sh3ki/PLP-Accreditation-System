# Clean Redeployment Guide
## PLP Accreditation System - Complete Fresh Deployment

This guide will help you completely remove the existing deployment and redeploy from scratch.

---

## ⚠️ WARNING
**This will delete ALL files on the server!**
- All application code
- All logs
- All configurations
- Database will NOT be affected (Firestore is cloud-based)

Make sure you have:
1. Backed up any custom configurations
2. Noted down your `.env` variables
3. Firebase credentials file

---

## Prerequisites

### 1. Prepare Your Environment Variables
Create a `.env` file locally with these variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=plpaccreditation.com,www.plpaccreditation.com
DATABASE_URL=sqlite:///db.sqlite3

# Firebase Configuration
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cloudinary (if used)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 2. Prepare Firebase Service Account File
Make sure you have `firebase-service-account.json` ready.

---

## Step-by-Step Deployment

### Step 1: Upload Scripts to Server

From your local machine:

```powershell
# Make scripts executable locally
cd "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\deployment"

# Upload to server
scp clean_and_redeploy.sh root@72.60.41.211:/tmp/
scp fresh_deploy.sh root@72.60.41.211:/tmp/
```

### Step 2: Connect to Server

```powershell
ssh root@72.60.41.211
```

### Step 3: Run Clean-up Script

```bash
# Make scripts executable
chmod +x /tmp/clean_and_redeploy.sh
chmod +x /tmp/fresh_deploy.sh

# Run cleanup
/tmp/clean_and_redeploy.sh
```

This will:
- ✓ Stop all services
- ✓ Remove application directory
- ✓ Remove service files
- ✓ Remove nginx configuration
- ✓ Remove logs
- ✓ Clean systemd

### Step 4: Prepare for Fresh Deployment

```bash
# Switch to plpadmin user
su - plpadmin

# Move fresh deploy script
mv /tmp/fresh_deploy.sh ~/
chmod +x ~/fresh_deploy.sh
```

### Step 5: Upload Configuration Files

From your **local machine** (new PowerShell window):

```powershell
# Upload .env file
scp "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\.env" plpadmin@72.60.41.211:/tmp/

# Upload Firebase credentials
scp "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\firebase-service-account.json" plpadmin@72.60.41.211:/tmp/
```

### Step 6: Run Fresh Deployment

Back on the **server** (as plpadmin):

```bash
# Run deployment script
~/fresh_deploy.sh
```

The script will:
1. ✓ Install system dependencies
2. ✓ Clone repository
3. ✓ Create virtual environment
4. ✓ Install Python packages
5. ✓ Set up environment variables
6. ✓ Collect static files
7. ✓ Create gunicorn service
8. ✓ Configure nginx
9. ✓ Start all services

### Step 7: Move Configuration Files

```bash
# Move .env file to project directory
mv /tmp/.env ~/PLP-Accreditation-System/accreditation/

# Move Firebase credentials
mv /tmp/firebase-service-account.json ~/PLP-Accreditation-System/accreditation/

# Set proper permissions
chmod 600 ~/PLP-Accreditation-System/accreditation/.env
chmod 600 ~/PLP-Accreditation-System/accreditation/firebase-service-account.json
```

### Step 8: Restart Services

```bash
# Restart gunicorn to load new environment
sudo systemctl restart gunicorn

# Check status
sudo systemctl status gunicorn
```

### Step 9: Verify Deployment

```bash
# Check logs for errors
sudo tail -f /var/log/plp_accreditation.err.log

# Test the application
curl -I https://plpaccreditation.com
```

---

## Quick Commands Reference

### Check Service Status
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### View Logs
```bash
# Error logs
sudo tail -f /var/log/plp_accreditation.err.log

# Access logs
sudo tail -f /var/log/plp_accreditation.access.log

# Last 100 lines
sudo tail -n 100 /var/log/plp_accreditation.err.log
```

### Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Stop Services
```bash
sudo systemctl stop gunicorn
sudo systemctl stop nginx
```

---

## Troubleshooting

### Issue: Gunicorn won't start

**Check:**
```bash
# View full status
sudo systemctl status gunicorn -l

# Check for errors
sudo journalctl -u gunicorn -n 50 --no-pager
```

**Common fixes:**
- Verify `.env` file exists and has correct permissions
- Check virtual environment is properly activated
- Ensure all dependencies are installed

### Issue: 502 Bad Gateway

**Causes:**
- Gunicorn not running
- Wrong socket/port configuration
- Nginx can't connect to gunicorn

**Fix:**
```bash
# Restart both services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Issue: Static files not loading

**Fix:**
```bash
cd ~/PLP-Accreditation-System/accreditation
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Issue: Still getting Quota Exceeded Error

**This is a Firebase/Firestore issue, not deployment!**

Solutions:
1. **Check Firebase Console:** https://console.firebase.google.com
   - Go to your project
   - Check Usage & Billing tab
   - View Firestore usage

2. **Upgrade to Blaze Plan:**
   - Firebase free tier has strict daily limits
   - Upgrade to pay-as-you-go (Blaze plan)
   - Set budget alerts

3. **Optimize queries:**
   - Add caching
   - Reduce unnecessary reads
   - Use compound queries

---

## Post-Deployment Checklist

- [ ] Application loads at https://plpaccreditation.com
- [ ] Can access login page
- [ ] Static files loading correctly
- [ ] Can login successfully
- [ ] Check error logs (should be minimal)
- [ ] Test key features (upload, download, etc.)
- [ ] Verify SSL certificate is working
- [ ] Check Firebase connection

---

## Need Help?

1. Check logs first: `sudo tail -f /var/log/plp_accreditation.err.log`
2. Check service status: `sudo systemctl status gunicorn`
3. Review nginx errors: `sudo tail -f /var/log/nginx/error.log`

---

**Remember:** The quota exceeded error is a **Firebase limitation**, not a deployment issue. Even after redeployment, you'll need to address Firebase quota limits!
