# PLP Accreditation System - Production Deployment Guide

## Server Information
- **VPS**: Hostinger KVM1
- **Domain**: plpaccreditation.com
- **OS**: Ubuntu/Debian Linux

## Quick Reference Commands

### Application Management
```bash
# Check application status
sudo supervisorctl status plp_accreditation

# Restart application
sudo supervisorctl restart plp_accreditation

# Stop application
sudo supervisorctl stop plp_accreditation

# Start application
sudo supervisorctl start plp_accreditation

# View application logs
sudo tail -f /var/log/plp_accreditation.out.log
sudo tail -f /var/log/plp_accreditation.err.log
```

### Nginx Management
```bash
# Check Nginx status
sudo systemctl status nginx

# Restart Nginx
sudo systemctl restart nginx

# Test Nginx configuration
sudo nginx -t

# View Nginx access logs
sudo tail -f /var/log/nginx/access.log

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Database Management
```bash
# Access PostgreSQL
sudo -u postgres psql

# Connect to PLP database
sudo -u postgres psql -d plp_accreditation

# Backup database
sudo -u postgres pg_dump plp_accreditation > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
sudo -u postgres psql plp_accreditation < backup_file.sql
```

### Django Management
```bash
# Navigate to project
cd /home/plpadmin/PLP-Accreditation-System/accreditation

# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Open Django shell
python manage.py shell
```

### SSL Certificate Management (Certbot)
```bash
# Renew SSL certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificate expiry
sudo certbot certificates
```

### Update Application
```bash
# Run deployment script
cd /home/plpadmin/PLP-Accreditation-System/accreditation/deployment
bash deploy.sh
```

## Troubleshooting

### Application Not Starting
1. Check supervisor logs: `sudo tail -f /var/log/plp_accreditation.err.log`
2. Verify virtual environment: `source venv/bin/activate`
3. Test Gunicorn manually: `gunicorn --bind 0.0.0.0:8000 accreditation.wsgi:application`

### 502 Bad Gateway
1. Check if Gunicorn is running: `sudo supervisorctl status`
2. Verify socket file exists: `ls -la /home/plpadmin/PLP-Accreditation-System/accreditation/gunicorn.sock`
3. Check Nginx error logs

### Static Files Not Loading
1. Collect static files: `python manage.py collectstatic`
2. Check permissions: `sudo chown -R plpadmin:www-data staticfiles/`
3. Verify Nginx configuration

### Database Connection Error
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify database credentials in .env file
3. Test connection: `sudo -u postgres psql -d plp_accreditation`

## Security Checklist
- [x] Firewall configured (UFW)
- [x] Non-root user created
- [x] SSL certificate installed
- [x] DEBUG=False in production
- [x] Strong SECRET_KEY set
- [x] Database credentials secured
- [x] Regular backups scheduled

## Monitoring
- Application logs: `/var/log/plp_accreditation.*.log`
- Nginx logs: `/var/log/nginx/`
- PostgreSQL logs: `/var/log/postgresql/`

## Backup Strategy
1. **Daily automated database backups**
2. **Weekly full system backups**
3. **Store backups off-server** (Hostinger Object Storage or external service)

## Contact & Support
- GitHub Repository: https://github.com/sh3ki/PLP-Accreditation-System
- Domain: https://plpaccreditation.com
