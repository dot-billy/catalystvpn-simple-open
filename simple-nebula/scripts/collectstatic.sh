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

echo "Collecting static files..."

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Activate virtual environment
source "$APP_DIR/venv/bin/activate"

# Collect static files
cd "$APP_DIR"
python manage.py collectstatic --noinput

# Set proper permissions
chown -R www-data:www-data "$APP_DIR/staticfiles"

echo "Static file collection complete!"
echo "Static files are located in: $APP_DIR/staticfiles" 