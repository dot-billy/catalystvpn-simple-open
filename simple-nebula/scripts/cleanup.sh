#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"

echo "Cleaning up temporary files and logs..."

# Clean up Python cache files
echo "Cleaning up Python cache files..."
find "$APP_DIR" -type d -name "__pycache__" -exec rm -r {} +
find "$APP_DIR" -type f -name "*.pyc" -delete
find "$APP_DIR" -type f -name "*.pyo" -delete
find "$APP_DIR" -type f -name "*.pyd" -delete
find "$APP_DIR" -type f -name ".coverage" -delete
find "$APP_DIR" -type d -name "htmlcov" -exec rm -r {} +
find "$APP_DIR" -type d -name ".pytest_cache" -exec rm -r {} +
find "$APP_DIR" -type d -name ".mypy_cache" -exec rm -r {} +

# Clean up Redis files
echo "Cleaning up Redis files..."
rm -f /var/run/redis/redis-server.pid
rm -f /var/log/redis/redis-server.log
rm -f /var/lib/redis/dump.rdb
rm -f /var/lib/redis/appendonly.aof

# Clean up RabbitMQ files
echo "Cleaning up RabbitMQ files..."
rm -f /var/run/rabbitmq/pid
rm -f /var/log/rabbitmq/*.log
rm -f /var/lib/rabbitmq/*.log

# Clean up Celery files
echo "Cleaning up Celery files..."
rm -f /var/run/celery/*.pid
rm -f /var/log/celery/*.log

# Clean up media files
echo "Cleaning up media files..."
rm -rf "$APP_DIR/media/*"

# Clean up static files
echo "Cleaning up static files..."
rm -rf "$APP_DIR/staticfiles/*"

# Clean up virtual environment
echo "Cleaning up virtual environment..."
rm -rf "$APP_DIR/venv"

echo "Cleanup complete." 