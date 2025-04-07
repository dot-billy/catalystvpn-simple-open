Deployment Guide
==============

This guide will help you deploy the Simple Nebula API to a production environment.

Prerequisites
-----------

* A production-grade server (e.g., Ubuntu 22.04 LTS)
* PostgreSQL 15 or higher
* Redis 7 or higher (optional, for caching)
* Python 3.8 or higher
* Nginx
* Gunicorn
* SSL certificate (recommended)

Server Setup
----------

1. Update the system:

   .. code-block:: bash

      sudo apt update
      sudo apt upgrade -y

2. Install required packages:

   .. code-block:: bash

      sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx redis-server

3. Configure PostgreSQL:

   .. code-block:: bash

      sudo -u postgres psql
      CREATE DATABASE nebula;
      CREATE USER nebula WITH PASSWORD 'your_secure_password';
      ALTER ROLE nebula SET client_encoding TO 'utf8';
      ALTER ROLE nebula SET default_transaction_isolation TO 'read committed';
      ALTER ROLE nebula SET timezone TO 'UTC';
      GRANT ALL PRIVILEGES ON DATABASE nebula TO nebula;
      \q

4. Create application directory:

   .. code-block:: bash

      sudo mkdir -p /var/www/nebula
      sudo chown -R $USER:$USER /var/www/nebula

5. Clone the repository:

   .. code-block:: bash

      cd /var/www/nebula
      git clone https://github.com/yourusername/simple-nebula.git .

6. Create and activate virtual environment:

   .. code-block:: bash

      python3 -m venv venv
      source venv/bin/activate

7. Install dependencies:

   .. code-block:: bash

      pip install -r requirements.txt
      pip install gunicorn

8. Create environment file:

   .. code-block:: bash

      cp .env.example .env
      # Edit .env with production settings

Example production `.env` file:

.. code-block:: text

   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=your-secure-secret-key
   DJANGO_ALLOWED_HOSTS=example.com,www.example.com
   CORS_ALLOWED_ORIGINS=https://example.com
   DATABASE_URL=postgres://nebula:your_secure_password@localhost:5432/nebula
   REDIS_URL=redis://localhost:6379/0

9. Run migrations:

   .. code-block:: bash

      python manage.py migrate

10. Collect static files:

    .. code-block:: bash

       python manage.py collectstatic --noinput

11. Create superuser:

    .. code-block:: bash

       python manage.py createsuperuser

Gunicorn Setup
------------

1. Create Gunicorn service file:

   .. code-block:: bash

      sudo nano /etc/systemd/system/nebula.service

2. Add the following content:

   .. code-block:: ini

      [Unit]
      Description=Gunicorn daemon for Simple Nebula API
      After=network.target

      [Service]
      User=www-data
      Group=www-data
      WorkingDirectory=/var/www/nebula
      Environment="PATH=/var/www/nebula/venv/bin"
      ExecStart=/var/www/nebula/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/nebula/nebula.sock \
          simple_nebula.wsgi:application

      [Install]
      WantedBy=multi-user.target

3. Start and enable the service:

   .. code-block:: bash

      sudo systemctl start nebula
      sudo systemctl enable nebula

Nginx Setup
---------

1. Create Nginx configuration:

   .. code-block:: bash

      sudo nano /etc/nginx/sites-available/nebula

2. Add the following content:

   .. code-block:: nginx

      server {
          listen 80;
          server_name example.com www.example.com;

          location = /favicon.ico { access_log off; log_not_found off; }
          
          location /static/ {
              root /var/www/nebula;
          }

          location /media/ {
              root /var/www/nebula;
          }

          location / {
              include proxy_params;
              proxy_pass http://unix:/var/www/nebula/nebula.sock;
          }
      }

3. Enable the site:

   .. code-block:: bash

      sudo ln -s /etc/nginx/sites-available/nebula /etc/nginx/sites-enabled/
      sudo nginx -t
      sudo systemctl restart nginx

SSL Setup
--------

1. Install Certbot:

   .. code-block:: bash

      sudo apt install -y certbot python3-certbot-nginx

2. Obtain SSL certificate:

   .. code-block:: bash

      sudo certbot --nginx -d example.com -d www.example.com

3. Certbot will automatically modify the Nginx configuration to use HTTPS.

Monitoring
---------

1. Install monitoring tools:

   .. code-block:: bash

      sudo apt install -y prometheus node-exporter

2. Configure Prometheus to monitor the application.

3. Set up log rotation:

   .. code-block:: bash

      sudo nano /etc/logrotate.d/nebula

4. Add the following content:

   .. code-block:: text

      /var/www/nebula/logs/*.log {
          daily
          rotate 14
          compress
          delaycompress
          missingok
          notifempty
          create 0640 www-data www-data
      }

Backup
-----

1. Create backup script:

   .. code-block:: bash

      sudo nano /usr/local/bin/backup-nebula.sh

2. Add the following content:

   .. code-block:: bash

      #!/bin/bash
      BACKUP_DIR="/var/backups/nebula"
      TIMESTAMP=$(date +%Y%m%d_%H%M%S)

      # Create backup directory if it doesn't exist
      mkdir -p $BACKUP_DIR

      # Backup database
      pg_dump -U nebula nebula > $BACKUP_DIR/db_$TIMESTAMP.sql

      # Backup media files
      tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz /var/www/nebula/media/

      # Keep only last 7 backups
      find $BACKUP_DIR -type f -mtime +7 -delete 