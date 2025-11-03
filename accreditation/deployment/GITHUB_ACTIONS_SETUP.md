# 🔐 GitHub Actions Auto-Deployment Setup Guide

## ✅ What This Does
Every time you push code to GitHub (master branch), it will **automatically**:
1. ✅ Pull latest code to your VPS server
2. ✅ Install new dependencies
3. ✅ Run database migrations
4. ✅ Collect static files
5. ✅ Restart Gunicorn & Nginx
6. ✅ Install LibreOffice (for PDF conversion)
7. ✅ Clear cache

**Result**: Your changes go live in ~2 minutes! 🚀

---

## 📋 Setup Instructions (ONE-TIME ONLY)

### Step 1: Add GitHub Secrets

1. Go to your GitHub repository: https://github.com/sh3ki/PLP-Accreditation-System

2. Click **Settings** → **Secrets and variables** → **Actions**

3. Click **New repository secret** and add these **3 secrets**:

#### Secret 1: `SERVER_HOST`
- Name: `SERVER_HOST`
- Value: `72.60.41.211`

#### Secret 2: `SERVER_USER`
- Name: `SERVER_USER`
- Value: `root`

#### Secret 3: `SERVER_PASSWORD`
- Name: `SERVER_PASSWORD`
- Value: `Accresystem2023@`

---

### Step 2: Push Workflow File to GitHub

Run these commands in your local terminal (PowerShell):

```powershell
cd "C:\Users\USER\Documents\SYSTEMS\WEB\PYTHON\DJANGO\PLP Accreditation System"

# Add the workflow file
git add .github/workflows/deploy.yml

# Commit
git commit -m "Add automated deployment workflow"

# Push to GitHub
git push origin master
```

---

### Step 3: Test Auto-Deployment

After pushing the workflow file, GitHub Actions will automatically run!

**Watch it live:**
1. Go to: https://github.com/sh3ki/PLP-Accreditation-System/actions
2. You'll see "Deploy to Hostinger VPS" running
3. Click it to watch real-time logs
4. Wait ~2 minutes
5. Check your site: http://72.60.41.211

---

## 🎯 How to Use (After Setup)

### Automatic Deployment (Recommended)
Just push your code normally:
```powershell
git add .
git commit -m "Your changes"
git push origin master
```
**That's it!** GitHub Actions will deploy automatically.

### Manual Deployment (Optional)
1. Go to: https://github.com/sh3ki/PLP-Accreditation-System/actions
2. Click "Deploy to Hostinger VPS"
3. Click "Run workflow" → "Run workflow"

---

## 📊 Monitor Deployments

**View deployment status:**
- GitHub Actions: https://github.com/sh3ki/PLP-Accreditation-System/actions
- Green ✅ = Success
- Red ❌ = Failed (click to see logs)

**Get notified:**
- GitHub will email you if deployment fails
- Fix the issue and push again

---

## 🔧 Troubleshooting

### Deployment Failed?
1. Click the failed workflow in GitHub Actions
2. Read the error logs
3. Fix the issue locally
4. Push again (it will auto-retry)

### Server Issues?
SSH into server manually:
```powershell
ssh root@72.60.41.211
# Password: Accresystem2023@

# Check service status
supervisorctl status plp_accreditation
systemctl status nginx

# View logs
tail -f /var/log/supervisor/plp_accreditation*.log
```

---

## ⚡ What Gets Deployed

**Included (Auto-deployed):**
- ✅ Python code changes
- ✅ Template changes
- ✅ Static files (CSS/JS)
- ✅ New dependencies
- ✅ Database migrations

**NOT Included (Manual):**
- ❌ Environment variables (`.env` file)
- ❌ Firebase credentials
- ❌ SSL certificates
- ❌ Server configuration changes

---

## 🎉 Success!

Your deployment is now **fully automated**!

**Before:** 
- SSH into server
- Git pull
- Install dependencies
- Restart services
- ~10 minutes manual work

**Now:**
- `git push origin master`
- Wait 2 minutes
- ☕ Done!

---

## 📝 Notes

- Deployments only run on `master` branch pushes
- Each deployment takes ~2 minutes
- You can track progress in GitHub Actions
- Failed deployments won't affect live site
- You can rollback by reverting Git commits

**Questions?** Check the deployment logs in GitHub Actions!
