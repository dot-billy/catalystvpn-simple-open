# Deployment Guide

This document provides instructions for deploying Simple Nebula in production environments.

## Production Deployment Checklist

Before deploying Simple Nebula to production, ensure you have:

- [ ] Set `DEBUG=False` in environment
- [ ] Configured proper secret keys
- [ ] Set up a production database (PostgreSQL)
- [ ] Configured proper CORS allowed origins
- [ ] Set up a proper web server (Nginx, etc.)
- [ ] Set up HTTPS with valid certificates
- [ ] Configured static file hosting
- [ ] Set up proper logging
- [ ] Planned for database backups

## Deployment Options

### Docker Compose

For a simple deployment using Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/dot-billy/catalystvpn-simple-open.git
   cd catalystvpn-simple-open/simple-nebula
   ```

2. Create a `.env` file for environment variables:
   ```
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=your-secure-secret-key
   DJANGO_ALLOWED_HOSTS=example.com,www.example.com
   CORS_ALLOWED_ORIGINS=https://example.com,https://app.example.com
   
   # Database
   POSTGRES_DB=nebula
   POSTGRES_USER=nebula
   POSTGRES_PASSWORD=secure-password
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   
   # Redis
   REDIS_URL=redis://redis:6379/0
   
   # JWT
   JWT_ACCESS_TOKEN_LIFETIME=60
   JWT_REFRESH_TOKEN_LIFETIME=1440
   ```

3. Start the services:
   ```bash
   docker compose up -d
   ```

4. Create a superuser:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

### Manual Deployment

For a manual deployment:

1. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export DJANGO_DEBUG=False
   export DJANGO_SECRET_KEY=your-secure-secret-key
   export DJANGO_ALLOWED_HOSTS=example.com,www.example.com
   export CORS_ALLOWED_ORIGINS=https://example.com
   export DATABASE_URL=postgres://user:password@localhost:5432/nebula
   export REDIS_URL=redis://localhost:6379/0
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. Set up Gunicorn:
   ```bash
   gunicorn nebula_django.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```

## Nginx Configuration

We recommend using Nginx as a reverse proxy in front of Gunicorn. Here's a sample configuration:

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Set max upload size
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /var/www/simple-nebula/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /media/ {
        alias /var/www/simple-nebula/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Proxy requests to Gunicorn
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
}
```

## Systemd Configuration

For a more robust deployment, use systemd to manage the Gunicorn process:

1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/nebula.service
   ```

2. Add the following content:
   ```ini
   [Unit]
   Description=Simple Nebula API
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/simple-nebula
   Environment="PATH=/var/www/simple-nebula/venv/bin"
   Environment="DJANGO_DEBUG=False"
   Environment="DJANGO_SECRET_KEY=your-secure-secret-key"
   Environment="DJANGO_ALLOWED_HOSTS=example.com,www.example.com"
   Environment="CORS_ALLOWED_ORIGINS=https://example.com"
   Environment="DATABASE_URL=postgres://user:password@localhost:5432/nebula"
   Environment="REDIS_URL=redis://localhost:6379/0"
   ExecStart=/var/www/simple-nebula/venv/bin/gunicorn \
       --workers 3 \
       --bind unix:/var/www/simple-nebula/nebula.sock \
       nebula_django.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl enable nebula
   sudo systemctl start nebula
   ```

## Scaling Considerations

### Database

For larger deployments:
- Consider a managed PostgreSQL service
- Set up read replicas if needed
- Implement connection pooling (e.g., pgBouncer)

### Caching

Enable Redis for caching:
- Session caching
- Query result caching
- API throttling

### Web Server

For high traffic:
- Increase the number of Gunicorn workers
- Use a load balancer with multiple application servers
- Configure worker timeouts appropriately

## Monitoring

We recommend setting up monitoring for:
- Application health
- Database performance
- Server resources (CPU, memory, disk space)

Consider tools like:
- Prometheus and Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- CloudWatch (AWS)
- NewRelic or Datadog 