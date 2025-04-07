#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"

echo "Formatting code..."

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Activate virtual environment
source "$APP_DIR/venv/bin/activate"

# Format code with Black
echo "Running Black..."
cd "$APP_DIR"
black .

# Sort imports with isort
echo "Running isort..."
isort .

# Run flake8
echo "Running flake8..."
flake8 .

# Run mypy
echo "Running mypy..."
mypy .

echo "Code formatting complete!" 