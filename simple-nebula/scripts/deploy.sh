#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
REPO_URL="https://github.com/yourusername/simple-nebula.git"
BRANCH="main"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

echo "Deploying Simple Nebula API..."

# Create application directory if it doesn't exist
if [ ! -d "$APP_DIR" ]; then
    echo "Creating application directory..."
    mkdir -p "$APP_DIR"
    chown -R www-data:www-data "$APP_DIR"
fi

# Clone or pull repository
if [ ! -d "$APP_DIR/.git" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
else
    echo "Pulling latest changes..."
    cd "$APP_DIR"
    git pull origin "$BRANCH"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "$APP_DIR/.env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env with your production settings"
    exit 1
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Restart Gunicorn
echo "Restarting Gunicorn..."
systemctl restart "$APP_NAME"

# Reload Nginx
echo "Reloading Nginx..."
systemctl reload nginx

echo "Deployment complete!"
echo "Please check the logs for any errors:"
echo "journalctl -u $APP_NAME" 