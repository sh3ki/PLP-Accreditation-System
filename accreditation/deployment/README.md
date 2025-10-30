# Deployment Files for PLP Accreditation System

This directory contains all necessary configuration files and scripts for deploying the PLP Accreditation System to production on Hostinger KVM1 VPS.

## 📁 Files Overview

### Configuration Files
- **`nginx_plp_accreditation`** - Nginx web server configuration
- **`supervisor_plp_accreditation.conf`** - Supervisor process manager configuration for Gunicorn
- **`.env.example`** - Template for environment variables (copy to `.env` and fill in)

### Scripts
- **`deploy.sh`** - Automated deployment script for updates
- **`generate_secret_key.py`** - Generate secure Django SECRET_KEY

### Documentation
- **`DEPLOYMENT_CHECKLIST.md`** - Complete checklist for deployment process
- **`DEPLOYMENT_COMMANDS.md`** - Step-by-step commands to run on server
- **`PRODUCTION_GUIDE.md`** - Production server management guide
- **`README.md`** - This file

## 🚀 Quick Start

### 1. First-Time Deployment
Follow the complete guide in **DEPLOYMENT_CHECKLIST.md**

### 2. Generate SECRET_KEY
On your local machine:
```bash
cd deployment
python generate_secret_key.py
```
Copy the output for your `.env` file.

### 3. Update Application (After Initial Deployment)
On your VPS:
```bash
cd /home/plpadmin/PLP-Accreditation-System/accreditation/deployment
bash deploy.sh
```

## 📋 Deployment Order

1. **Read**: `DEPLOYMENT_CHECKLIST.md` - Understand the full process
2. **Follow**: Complete Phases 1-6 (server setup, software installation, database)
3. **Configure**: Copy and modify configuration files
4. **Run**: Commands from `DEPLOYMENT_COMMANDS.md`
5. **Reference**: `PRODUCTION_GUIDE.md` for ongoing management

## 🔐 Environment Variables

Create a `.env` file in the `accreditation` directory with:

```env
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=plpaccreditation.com,www.plpaccreditation.com,YOUR_VPS_IP

DB_ENGINE=django.db.backends.postgresql
DB_NAME=plp_accreditation
DB_USER=plpuser
DB_PASSWORD=your-strong-database-password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=accreditationsystem2023@gmail.com
EMAIL_HOST_PASSWORD=tjgh wibm ddtg eqml
```

## 🛠️ Server Requirements

- **OS**: Ubuntu 20.04+ or Debian 11+
- **Python**: 3.8+
- **Database**: PostgreSQL 12+
- **Web Server**: Nginx
- **Process Manager**: Supervisor
- **WSGI Server**: Gunicorn
- **SSL**: Let's Encrypt (Certbot)

## 📝 Important Notes

1. **Never commit `.env` file to Git** - It contains sensitive credentials
2. **Use strong passwords** for database and Django admin
3. **Keep DEBUG=False** in production
4. **Regular backups** are essential
5. **Monitor logs** regularly for errors
6. **Update dependencies** periodically for security

## 🔍 Troubleshooting

See **PRODUCTION_GUIDE.md** for:
- Common issues and solutions
- Log file locations
- Service management commands
- Database backup/restore procedures

## 🔗 Useful Links

- **Production URL**: https://plpaccreditation.com
- **GitHub Repository**: https://github.com/sh3ki/PLP-Accreditation-System
- **Hostinger Support**: https://www.hostinger.com/contact

## 📞 Support

For deployment issues:
1. Check logs: `/var/log/plp_accreditation.err.log`
2. Review troubleshooting section in `PRODUCTION_GUIDE.md`
3. Check Nginx logs: `/var/log/nginx/error.log`
4. Verify Supervisor status: `sudo supervisorctl status`

---

**Last Updated**: October 30, 2025
**Maintainer**: PLP Accreditation Team
