#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"

echo "Starting Redis server..."

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Start Redis server
redis-server \
    --port 6379 \
    --daemonize yes \
    --pidfile /var/run/redis/redis-server.pid \
    --logfile /var/log/redis/redis-server.log \
    --dir /var/lib/redis \
    --appendonly yes \
    --appendfsync everysec \
    --no-appendfsync-on-rewrite yes \
    --auto-aof-rewrite-percentage 100 \
    --auto-aof-rewrite-min-size 64mb 