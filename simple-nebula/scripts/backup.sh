#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
BACKUP_DIR="/var/backups/$APP_NAME"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

echo "Starting backup process..."

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Creating backup directory..."
    mkdir -p "$BACKUP_DIR"
    chown -R www-data:www-data "$BACKUP_DIR"
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

# Backup database
echo "Backing up database..."
PGPASSWORD=$DB_PASS pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > "$BACKUP_DIR/db_$TIMESTAMP.sql"

# Backup media files
echo "Backing up media files..."
tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" "/var/www/$APP_NAME/media/"

# Keep only last 7 backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -type f -mtime +7 -delete

echo "Backup complete!"
echo "Backup files:"
echo "- Database: $BACKUP_DIR/db_$TIMESTAMP.sql"
echo "- Media: $BACKUP_DIR/media_$TIMESTAMP.tar.gz" 