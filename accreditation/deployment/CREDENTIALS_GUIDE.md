# Important: Third-Party Service Credentials

## 🔐 Services Used in Production

Your PLP Accreditation System uses the following third-party services. **You will continue using your existing credentials** for all of these:

### 1. **Firebase** (Authentication & Database)
- **Project**: `plp-accreditation`
- **Project Number**: `659742231759`
- **Service**: Firebase Authentication + Firestore Database
- **Configuration**: 
  - Upload your existing `firebase-service-account.json` file to the server
  - Path on server: `/home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json`
  - No additional configuration needed - same credentials work in production

### 2. **Cloudinary** (File/Image Storage)
- **Cloud Name**: `dygrh6ztt` (hardcoded in `cloudinary_utils.py`)
- **Service**: Image and file hosting
- **Required in .env**:
  ```env
  CLOUDINARY_API_KEY=your-api-key
  CLOUDINARY_API_SECRET=your-api-secret
  ```
- **Where to find credentials**: https://cloudinary.com/console
  - Login to your Cloudinary account
  - Dashboard shows: Cloud name, API Key, API Secret
  - Copy API Key and API Secret to your server's `.env` file

### 3. **Gmail SMTP** (Email/OTP)
- **Email**: `accreditationsystem2023@gmail.com`
- **App Password**: `tjgh wibm ddtg eqml`
- **Service**: Sending OTP verification emails
- **Already configured**: Email credentials are already in the deployment files

---

## 📝 What You Need to Do During Deployment

### Step 1: Upload Firebase Service Account JSON
When you're setting up the server, you'll need to upload your existing `firebase-service-account.json` file:

**Option A - Using SCP (from your local machine):**
```powershell
scp "c:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System\accreditation\firebase-service-account.json" plpadmin@YOUR_VPS_IP:/home/plpadmin/PLP-Accreditation-System/accreditation/
```

**Option B - Copy/Paste:**
1. Open the local file
2. Copy its contents
3. On server: `nano /home/plpadmin/PLP-Accreditation-System/accreditation/firebase-service-account.json`
4. Paste and save

### Step 2: Add Cloudinary Credentials to .env
When creating your `.env` file on the server, add your Cloudinary credentials:

1. Login to https://cloudinary.com/console
2. Find your Dashboard
3. Copy **API Key** and **API Secret**
4. Add to server's `.env` file:
   ```env
   CLOUDINARY_API_KEY=your-actual-api-key
   CLOUDINARY_API_SECRET=your-actual-api-secret
   ```

### Step 3: Email Configuration (Already Set)
The Gmail credentials are already configured and will work automatically. No changes needed!

---

## ✅ Production .env File Example

Your complete `.env` file on the server should look like this:

```env
# Django Security
SECRET_KEY=your-generated-secret-key-from-script
DEBUG=False
ALLOWED_HOSTS=plpaccreditation.com,www.plpaccreditation.com,YOUR_VPS_IP

# PostgreSQL Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=plp_accreditation
DB_USER=plpuser
DB_PASSWORD=your-strong-database-password
DB_HOST=localhost
DB_PORT=5432

# Email (existing credentials - keep as-is)
EMAIL_HOST_USER=accreditationsystem2023@gmail.com
EMAIL_HOST_PASSWORD=tjgh wibm ddtg eqml

# Cloudinary (get from https://cloudinary.com/console)
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz123456
```

---

## 🚨 Important Security Notes

1. **Never commit these files to Git**:
   - `firebase-service-account.json` ✅ Already in `.gitignore`
   - `.env` ✅ Already in `.gitignore`

2. **Keep credentials secure**:
   - Don't share in chat, email, or public repositories
   - Use SSH/SCP for secure file transfer
   - Set proper file permissions on server: `chmod 600 .env firebase-service-account.json`

3. **Firebase continues to work**: 
   - Your existing Firebase data will be accessible
   - No migration needed
   - Same authentication works

4. **Cloudinary continues to work**:
   - All existing uploaded images remain accessible
   - Same storage, same URLs
   - No migration needed

---

## 🔍 Verification After Deployment

Once deployed, verify each service works:

1. **Firebase**: Login to the system - if authentication works, Firebase is connected
2. **Cloudinary**: Upload a profile image or document - if it works, Cloudinary is connected
3. **Email**: Request OTP verification - if email arrives, Gmail SMTP is working

---

## 📞 Where to Get Help

- **Firebase Console**: https://console.firebase.google.com/project/plp-accreditation
- **Cloudinary Dashboard**: https://cloudinary.com/console
- **Gmail App Passwords**: https://myaccount.google.com/apppasswords

---

**Summary**: You're keeping ALL your existing credentials. Nothing changes except you're adding them to the `.env` file on your production server so Django can access them.
