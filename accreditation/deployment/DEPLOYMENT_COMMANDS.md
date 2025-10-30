# Step-by-Step Production Deployment Commands

## After completing Phase 1-4 and configuring .env file, run these commands on your VPS:

### 1. Apply Django Migrations
```bash
cd /home/plpadmin/PLP-Accreditation-System/accreditation
source venv/bin/activate
python manage.py migrate
```

### 2. Create Django Superuser
```bash
python manage.py createsuperuser
```
Follow prompts to create admin account.

### 3. Collect Static Files
```bash
python manage.py collectstatic
```
Type 'yes' when prompted.

### 4. Set Proper Permissions
```bash
sudo chown -R plpadmin:www-data /home/plpadmin/PLP-Accreditation-System
sudo chmod -R 755 /home/plpadmin/PLP-Accreditation-System
```

### 5. Configure Supervisor
```bash
sudo cp /home/plpadmin/PLP-Accreditation-System/accreditation/deployment/supervisor_plp_accreditation.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start plp_accreditation
sudo supervisorctl status
```

### 6. Configure Nginx
```bash
sudo cp /home/plpadmin/PLP-Accreditation-System/accreditation/deployment/nginx_plp_accreditation /etc/nginx/sites-available/plp_accreditation
sudo ln -s /etc/nginx/sites-available/plp_accreditation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Install SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d plpaccreditation.com -d www.plpaccreditation.com
```
Follow prompts, provide email, agree to terms.

### 8. Test Your Site
Visit: https://plpaccreditation.com

### 9. Setup Automatic Certificate Renewal
```bash
sudo systemctl status certbot.timer
```
Should show active. Certificates auto-renew.

### 10. Make Deploy Script Executable
```bash
chmod +x /home/plpadmin/PLP-Accreditation-System/accreditation/deployment/deploy.sh
```

## Done! Your application is now live! 🎉
