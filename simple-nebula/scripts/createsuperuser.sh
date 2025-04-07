#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Get superuser details
read -p "Enter username for superuser: " USERNAME
read -p "Enter email for superuser: " EMAIL
read -s -p "Enter password for superuser: " PASSWORD
echo

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Activate virtual environment
source "$APP_DIR/venv/bin/activate"

# Create superuser
cd "$APP_DIR"
python manage.py createsuperuser --username "$USERNAME" --email "$EMAIL" --noinput

# Set password
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
user = User.objects.get(username='$USERNAME');
user.set_password('$PASSWORD');
user.save();
"

echo "Superuser created successfully!"
echo "Username: $USERNAME"
echo "Email: $EMAIL" 