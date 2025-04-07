#!/bin/bash

# Exit on error
set -e

echo "Stopping all development services..."

# Stop development server
echo "Stopping development server..."
pkill -f "python manage.py runserver"

# Stop Flower monitoring
echo "Stopping Flower monitoring..."
pkill -f "celery -A simple_nebula flower"

# Stop Celery beat
echo "Stopping Celery beat..."
pkill -f "celery -A simple_nebula beat"

# Stop Celery worker
echo "Stopping Celery worker..."
pkill -f "celery -A simple_nebula worker"

# Stop RabbitMQ server
echo "Stopping RabbitMQ server..."
rabbitmqctl stop

# Stop Redis server
echo "Stopping Redis server..."
redis-cli shutdown

echo "All services stopped." 