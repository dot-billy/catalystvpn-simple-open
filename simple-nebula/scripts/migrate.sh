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

echo "Running database migrations..."

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Activate virtual environment
source "$APP_DIR/venv/bin/activate"

# Run migrations
cd "$APP_DIR"
python manage.py migrate

echo "Database migrations complete!"
echo "Please check the application logs for any errors:"
echo "journalctl -u $APP_NAME" 