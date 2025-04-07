#!/bin/bash

# Exit on error
set -e

echo "Checking status of all development services..."

# Check Redis server
echo "Checking Redis server..."
if pgrep -f "redis-server" > /dev/null; then
    echo "Redis server is running"
    redis-cli ping
else
    echo "Redis server is not running"
fi

# Check RabbitMQ server
echo "Checking RabbitMQ server..."
if pgrep -f "beam.smp" > /dev/null; then
    echo "RabbitMQ server is running"
    rabbitmqctl status
else
    echo "RabbitMQ server is not running"
fi

# Check Celery worker
echo "Checking Celery worker..."
if pgrep -f "celery -A simple_nebula worker" > /dev/null; then
    echo "Celery worker is running"
else
    echo "Celery worker is not running"
fi

# Check Celery beat
echo "Checking Celery beat..."
if pgrep -f "celery -A simple_nebula beat" > /dev/null; then
    echo "Celery beat is running"
else
    echo "Celery beat is not running"
fi

# Check Flower monitoring
echo "Checking Flower monitoring..."
if pgrep -f "celery -A simple_nebula flower" > /dev/null; then
    echo "Flower monitoring is running"
else
    echo "Flower monitoring is not running"
fi

# Check development server
echo "Checking development server..."
if pgrep -f "python manage.py runserver" > /dev/null; then
    echo "Development server is running"
else
    echo "Development server is not running"
fi 