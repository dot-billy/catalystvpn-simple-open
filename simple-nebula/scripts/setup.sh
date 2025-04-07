#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"

echo "Setting up development environment..."

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p "$APP_DIR"
mkdir -p /var/run/redis
mkdir -p /var/log/redis
mkdir -p /var/lib/redis
mkdir -p /var/run/rabbitmq
mkdir -p /var/log/rabbitmq
mkdir -p /var/lib/rabbitmq
mkdir -p /var/run/celery
mkdir -p /var/log/celery
mkdir -p "$APP_DIR/media"
mkdir -p "$APP_DIR/staticfiles"

# Set up virtual environment
echo "Setting up virtual environment..."
python3 -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install -r "$APP_DIR/requirements.txt"

# Install system dependencies
echo "Installing system dependencies..."
if [ "$(uname)" == "Darwin" ]; then
    # macOS
    brew install redis rabbitmq
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux
    sudo apt-get update
    sudo apt-get install -y redis-server rabbitmq-server
fi

# Set up environment variables
echo "Setting up environment variables..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo "Please update .env file with your configuration"
fi

# Run database migrations
echo "Running database migrations..."
cd "$APP_DIR"
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Set up Celery
echo "Setting up Celery..."
python manage.py shell -c "from django_celery_beat.models import PeriodicTask, IntervalSchedule; schedule, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.MINUTES); PeriodicTask.objects.get_or_create(name='Check for expired certificates', task='api.tasks.check_expired_certificates', schedule=schedule)"

# Set permissions
echo "Setting permissions..."
chmod -R 755 "$APP_DIR"
chown -R $USER:$USER "$APP_DIR"

echo "Development environment setup complete."
echo "Please run './scripts/runall.sh' to start all services." 