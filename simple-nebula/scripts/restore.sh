#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
BACKUP_DIR="/var/backups/$APP_NAME"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -l "$BACKUP_DIR"/*.sql
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load environment variables
if [ -f "/var/www/$APP_NAME/.env" ]; then
    source "/var/www/$APP_NAME/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Extract database credentials from DATABASE_URL
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^/]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)/\1/p')

# Stop the application
echo "Stopping application..."
systemctl stop "$APP_NAME"

# Drop and recreate database
echo "Dropping and recreating database..."
PGPASSWORD=$DB_PASS dropdb -h $DB_HOST -U $DB_USER $DB_NAME || true
PGPASSWORD=$DB_PASS createdb -h $DB_HOST -U $DB_USER $DB_NAME

# Restore database
echo "Restoring database from backup..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER $DB_NAME < "$BACKUP_FILE"

# Start the application
echo "Starting application..."
systemctl start "$APP_NAME"

echo "Database restoration complete!"
echo "Please check the application logs for any errors:"
echo "journalctl -u $APP_NAME" 