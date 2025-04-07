FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client wget \
    && rm -rf /var/lib/apt/lists/*

# Download, untar and move nebula and nebula-cert to /usr/local/bin
RUN mkdir -p /tmp/nebula && \
    cd /tmp/nebula && \
    wget https://github.com/slackhq/nebula/releases/download/v1.9.5/nebula-linux-amd64.tar.gz && \
    tar -xzf nebula-linux-amd64.tar.gz && \
    mv nebula /usr/local/bin/ && \
    mv nebula-cert /usr/local/bin/ && \
    chmod +x /usr/local/bin/nebula && \
    chmod +x /usr/local/bin/nebula-cert && \
    cd / && \
    rm -rf /tmp/nebula

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "nebula_django.wsgi:application", "--bind", "0.0.0.0:8000"] 