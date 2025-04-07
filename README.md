# Catalyst VPN Simple Open

A monorepo containing the complete Catalyst VPN Simple Open solution, including frontend, backend, and related services.

### Note;

We are currently working this under branches with nothing being published to main just yet. Current working branch is 04-06-2025

## Project Structure

This is a monorepo containing multiple components:

- `simple-frontend/`: React-based frontend application
- `simple-nebula/`: Django-based backend API service
- `simple-go/`: Go-based CLI tools and utilities

## Environment Variables

The project uses several environment variables for configuration. Here's a breakdown of the key variables:

### API Configuration
- `API_BASE_URL`: The base URL for the API server (default: http://localhost:8000)
- `myBackEndUrlOrIP`: The IP address or hostname of your backend server (replaces 10.45.0.16)

### Frontend Configuration
- `REACT_APP_API_URL`: The full API URL for the React frontend (default: http://myBackEndUrlOrIP:8000/api)
- `REACT_APP_URL`: http://myappurl:3000

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

## Contributing

We welcome contributions to Catalyst VPN - Open! Here's how you can help:

### Development Setup

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment for each component

### Pull Request Guidelines

1. Create a new branch for your feature/fix
2. Make your changes
3. Test your changes
4. Update documentation as needed
5. Submit a pull request with a clear description of changes

### Code Style

- Make it usable and readable.

### Documentation

- Update README files as needed
- Add comments for complex logic
- Document any new environment variables
- Update API documentation if endpoints change

### Security

- Report security vulnerabilities responsibly
- Follow security best practices
- Never commit sensitive information
- Use environment variables for configuration

### Issue Reporting

- Use the issue tracker to report bugs
- Provide detailed reproduction steps
- Include environment information
- Check for existing issues before creating new ones

Note: React environment variables must be prefixed with `REACT_APP_` and are embedded at build time. Make sure to rebuild the frontend after changing these variables.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Variables

- `django_superuser` is replaced with: `myadminemail@gmail.com`
- `django_superuser_password` is replaced with: `myAdminPassword`
- `10.45.0.16` is replaced with: `myBackEndUrlOrIP`
