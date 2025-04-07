#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"

echo "Starting all development services..."

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Create necessary directories
mkdir -p /var/run/redis
mkdir -p /var/log/redis
mkdir -p /var/lib/redis

# Start Redis server
echo "Starting Redis server..."
./scripts/runredis.sh &

# Start RabbitMQ server
echo "Starting RabbitMQ server..."
./scripts/runrabbitmq.sh &

# Wait for services to start
sleep 5

# Start Celery worker
echo "Starting Celery worker..."
./scripts/runworker.sh &

# Start Celery beat
echo "Starting Celery beat..."
./scripts/runbeat.sh &

# Start Flower monitoring
echo "Starting Flower monitoring..."
./scripts/runflower.sh &

# Start development server
echo "Starting development server..."
./scripts/runserver.sh 