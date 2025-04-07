# Catalyst VPN Simple Open

## Environment Variables

The project uses several environment variables for configuration. Here's a breakdown of the key variables:

### API Configuration
- `API_BASE_URL`: The base URL for the API server (default: http://localhost:8000)
- `myBackEndUrlOrIP`: The IP address or hostname of your backend server (replaces 10.45.0.16)

### Frontend Configuration
- `REACT_APP_API_URL`: The full API URL for the React frontend (default: http://myBackEndUrlOrIP:8000/api)
-  `REACT_APP_URL` : http://myappurl:3000

### Backend Configuration
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts for the Django backend
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS
- `myadminemail@gmail.com`: Admin email for Django superuser
- `myAdminPassword`: Admin password for Django superuser

### Database Configuration
- `POSTGRES_PASSWORD`: Database password
- `DATABASE_URL`: Database connection URL

### Security Configuration
- `SECRET_KEY`: Django secret key for security
- `DJANGO_DEBUG`: Django debug mode (True/False)

## Setup Instructions

1. Replace the following placeholders in your environment:
   - `myBackEndUrlOrIP` with your actual backend server IP/hostname
   - `myadminemail@gmail.com` with your admin email
   - `myAdminPassword` with your secure admin password

2. For development:
   - Use default values for most variables
   - Set `DJANGO_DEBUG=True`
   - Use `localhost` or `127.0.0.1` for local development

3. For production:
   - Set appropriate values for `API_BASE_URL` and `myBackEndUrlOrIP`
   - Change all default passwords
   - Set `DJANGO_DEBUG=False`
   - Generate a secure `SECRET_KEY`
   - Configure proper `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`

Note: React environment variables must be prefixed with `REACT_APP_` and are embedded at build time. Make sure to rebuild the frontend after changing these variables.

Variables: 
django_superuser is replaced with: myadminemail@gmail.com
django_superuser_password is replaced with: myAdminPassword
10.45.0.16 is replaced with: myBackEndUrlOrIP




