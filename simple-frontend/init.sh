#!/bin/bash

# Create necessary directories
mkdir -p src/components
mkdir -p src/pages
mkdir -p src/services
mkdir -p public

# Install dependencies
npm install

# Create React app
npx create-react-app . --template typescript

# Install additional dependencies
npm install @emotion/react @emotion/styled @mui/material @mui/icons-material @reduxjs/toolkit @tanstack/react-query axios formik yup react-router-dom @types/node web-vitals

# Build the Docker container
docker-compose build

echo "Project initialization complete! Run 'docker-compose up' to start the development server." 