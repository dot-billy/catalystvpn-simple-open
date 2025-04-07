#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"

echo "Starting Celery worker..."

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Activate virtual environment
source "$APP_DIR/venv/bin/activate"

# Start Celery worker
cd "$APP_DIR"
celery -A simple_nebula worker \
    --loglevel=INFO \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --max-memory-per-child=512000 \
    --prefetch-multiplier=1 