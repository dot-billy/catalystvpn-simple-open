#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"

echo "Starting RabbitMQ server..."

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Start RabbitMQ server
rabbitmq-server \
    -detached \
    -setcookie rabbit \
    -sname rabbit@localhost \
    -rabbitmq_management listener [{port,15672}] \
    -rabbit tcp_listeners [5672] \
    -rabbit loopback_users [] \
    -rabbit default_vhost "/" \
    -rabbit default_user "guest" \
    -rabbit default_pass "guest" 