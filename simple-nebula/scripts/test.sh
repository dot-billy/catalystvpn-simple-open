#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"

echo "Running tests..."

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Activate virtual environment
source "$APP_DIR/venv/bin/activate"

# Run tests with coverage
cd "$APP_DIR"
coverage run manage.py test api.tests
coverage report
coverage html

# Run type checking
echo "Running type checking..."
mypy api

# Run linting
echo "Running linting..."
flake8 api
black --check api
isort --check-only api

echo "Tests complete." 