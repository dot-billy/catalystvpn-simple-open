#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="nebula"
APP_DIR="/var/www/$APP_NAME"
DOCS_DIR="$APP_DIR/docs"

echo "Building documentation..."

# Load environment variables
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
else
    echo "Error: .env file not found"
    exit 1
fi

# Activate virtual environment
source "$APP_DIR/venv/bin/activate"

# Build documentation
cd "$DOCS_DIR"
make html

echo "Documentation build complete!"
echo "Documentation is available in: $DOCS_DIR/_build/html/" 