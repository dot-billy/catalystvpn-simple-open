#!/bin/bash

# Exit on error
set -e

echo "Setting up Simple Nebula API development environment..."

# Check Python version
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env with your settings"
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py createsuperuser --noinput \
    --username admin \
    --email admin@example.com

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run tests
echo "Running tests..."
pytest

echo "Development environment setup complete!"
echo "To start the development server, run:"
echo "python manage.py runserver" 