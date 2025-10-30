# Complete Deployment Checklist for PLP Accreditation System

## Pre-Deployment Checklist
- [ ] GitHub repository is up to date
- [ ] Firebase service account JSON file is available
- [ ] Gmail app password is ready
- [ ] Domain plpaccreditation.com is registered
- [ ] KVM1 VPS is active on Hostinger
- [ ] VPS IP address noted down
- [ ] VPS root password available

## Phase 1: VPS Initial Setup
- [ ] Connected to VPS via SSH
- [ ] System updated (`apt update && apt upgrade`)
- [ ] Non-root user 'plpadmin' created
- [ ] Firewall (UFW) configured
- [ ] Firewall enabled

## Phase 2: Software Installation
- [ ] Python 3, pip, venv installed
- [ ] Build essentials installed
- [ ] Nginx installed and running
- [ ] PostgreSQL installed and running
- [ ] Supervisor installed and running
- [ ] Git installed

## Phase 3: Domain Configuration
- [ ] DNS A record for @ pointing to VPS IP
- [ ] DNS A record for www pointing to VPS IP
- [ ] DNS propagation verified (ping domain)

## Phase 4: Application Setup
- [ ] Switched to plpadmin user
- [ ] Repository cloned from GitHub
- [ ] Virtual environment created
- [ ] Python dependencies installed
- [ ] Gunicorn and psycopg2-binary installed

## Phase 5: Database Setup
- [ ] PostgreSQL database 'plp_accreditation' created
- [ ] Database user 'plpuser' created with strong password
- [ ] User granted all privileges on database
- [ ] Database connection tested

## Phase 6: Environment Configuration
- [ ] .env file created in accreditation directory
- [ ] SECRET_KEY generated and set
- [ ] DEBUG set to False
- [ ] ALLOWED_HOSTS configured
- [ ] Database credentials added to .env
- [ ] Email credentials verified in .env

## Phase 7: Firebase Setup
- [ ] Firebase service account JSON uploaded to server
- [ ] File path matches FIREBASE_SERVICE_ACCOUNT_PATH in settings
- [ ] File permissions set correctly

## Phase 8: Django Configuration
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Django superuser created
- [ ] Static files collected
- [ ] staticfiles directory created
- [ ] Permissions set on project directory

## Phase 9: Gunicorn & Supervisor
- [ ] Supervisor config file copied to /etc/supervisor/conf.d/
- [ ] Supervisor reread and updated
- [ ] Application started via supervisor
- [ ] Application status verified (running)
- [ ] Logs checked for errors

## Phase 10: Nginx Configuration
- [ ] Nginx config copied to sites-available
- [ ] Symbolic link created in sites-enabled
- [ ] Nginx configuration tested (`sudo nginx -t`)
- [ ] Nginx restarted
- [ ] Site accessible via HTTP

## Phase 11: SSL Certificate
- [ ] Certbot installed
- [ ] SSL certificate obtained for plpaccreditation.com
- [ ] SSL certificate obtained for www.plpaccreditation.com
- [ ] HTTPS redirect enabled
- [ ] Certificate auto-renewal verified

## Phase 12: Final Testing
- [ ] Site accessible via https://plpaccreditation.com
- [ ] Login page loads correctly
- [ ] Static files (CSS, JS) loading
- [ ] Database operations working
- [ ] Firebase authentication working
- [ ] File uploads working
- [ ] Email OTP working
- [ ] All pages navigable

## Phase 13: Security Hardening
- [ ] DEBUG=False verified
- [ ] Secret key is strong and unique
- [ ] Database password is strong
- [ ] SSH key authentication enabled (optional)
- [ ] Fail2ban installed (optional but recommended)
- [ ] Regular backups scheduled

## Phase 14: Monitoring Setup
- [ ] Supervisor logs accessible
- [ ] Nginx logs accessible
- [ ] Error monitoring in place
- [ ] Disk space monitoring
- [ ] Database backup script created

## Post-Deployment
- [ ] deployment/deploy.sh made executable
- [ ] Test deployment script
- [ ] Document custom configurations
- [ ] Share admin credentials securely
- [ ] Monitor for first 24 hours

## Common Issues & Solutions

### Issue: 502 Bad Gateway
**Solution**: 
```bash
sudo supervisorctl status plp_accreditation
sudo supervisorctl restart plp_accreditation
```

### Issue: Static files not loading
**Solution**:
```bash
python manage.py collectstatic --clear
sudo systemctl restart nginx
```

### Issue: Database connection error
**Solution**: Check .env file, verify PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

### Issue: Permission denied errors
**Solution**:
```bash
sudo chown -R plpadmin:www-data /home/plpadmin/PLP-Accreditation-System
sudo chmod -R 755 /home/plpadmin/PLP-Accreditation-System
```

## Emergency Contacts
- Hostinger Support: https://www.hostinger.com/contact
- GitHub Repository: https://github.com/sh3ki/PLP-Accreditation-System

## Backup Verification
- [ ] Test database backup and restore
- [ ] Verify backup storage location
- [ ] Test recovery procedure

---
**Deployment Date**: _______________
**Deployed By**: _______________
**Production URL**: https://plpaccreditation.com
