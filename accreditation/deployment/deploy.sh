#!/bin/bash
# Deployment script for PLP Accreditation System

echo "Starting deployment..."

# Navigate to project directory
cd /home/plpadmin/PLP-Accreditation-System/accreditation

# Activate virtual environment
source venv/bin/activate

# Pull latest changes from GitHub
echo "Pulling latest changes from GitHub..."
git pull origin master

# Install/Update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Restart Gunicorn
echo "Restarting application..."
sudo supervisorctl restart plp_accreditation

echo "Deployment completed successfully!"
