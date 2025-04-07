# User Management

This document describes the user management features in Simple Nebula.

## User Model

The Simple Nebula API uses a custom user model with email-based authentication instead of the default Django username-based authentication. Users have the following properties:

- **UUID**: Unique identifier (primary key)
- **Email**: Unique email address (used for authentication)
- **Full Name**: User's full name
- **Is Staff**: Boolean indicating admin access permission
- **Is Active**: Boolean indicating whether the account is active
- **Date Joined**: Timestamp of account creation

## Authentication

The API supports two authentication methods:

### JWT Authentication

JSON Web Tokens (JWT) are used for user authentication. The API provides two endpoints for JWT authentication:

1. **Obtain Token**: `POST /api/token/`
   - Request body: `{ "email": "user@example.com", "password": "password" }`
   - Response: `{ "access": "access_token", "refresh": "refresh_token", "user": {...} }`

2. **Refresh Token**: `POST /api/token/refresh/`
   - Request body: `{ "refresh": "refresh_token" }`
   - Response: `{ "access": "new_access_token", "refresh": "new_refresh_token" }`

### API Key Authentication

API keys can be generated for programmatic access, especially for nodes and lighthouses. API keys are included in the Authorization header:

```
Authorization: Api-Key <api_key>
```

## User Registration

New users can register by making a POST request to the `/api/users/` endpoint:

```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "full_name": "Example User",
    "password": "secure_password"
  }'
```

## User Profile

Authenticated users can retrieve their profile information using the `/api/users/me/` endpoint:

```bash
curl -X GET "http://localhost:8000/api/users/me/" \
  -H "Authorization: Bearer <access_token>"
```

## Managing Roles and Permissions

Users are associated with organizations through memberships, which include role information. The following roles are available:

### Roles

1. **Admin**
   - Can manage the organization (add/remove users, change settings)
   - Can manage all resources within the organization
   - Can assign roles to other users

2. **Operator**
   - Can manage resources (networks, nodes, lighthouses, security groups)
   - Cannot manage the organization itself or assign roles

3. **Viewer**
   - Read-only access to resources
   - Cannot make any changes

### Assigning Roles

Organization admins can assign roles to users through the membership API:

```bash
# Add a user to an organization with a specific role
curl -X POST "http://localhost:8000/api/organizations/<organization-slug>/members/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<user-uuid>",
    "role": "admin"  # or "operator" or "viewer"
  }'

# Update a user's role
curl -X PATCH "http://localhost:8000/api/organizations/<organization-slug>/members/<membership-id>/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "operator"
  }'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/` | GET | List all users (admin only) |
| `/api/users/` | POST | Create a new user (registration) |
| `/api/users/<uuid>/` | GET | Get user details |
| `/api/users/<uuid>/` | PATCH | Update user |
| `/api/users/<uuid>/` | DELETE | Delete user |
| `/api/users/me/` | GET | Get current user profile |
| `/api/token/` | POST | Obtain JWT tokens |
| `/api/token/refresh/` | POST | Refresh JWT token |
| `/api/roles/` | GET | Get available roles |
| `/api/organizations/<slug>/members/` | GET | List organization members |
| `/api/organizations/<slug>/members/` | POST | Add member to organization |
| `/api/organizations/<slug>/members/<uuid>/` | PATCH | Update member role |
| `/api/organizations/<slug>/members/<uuid>/` | DELETE | Remove member from organization | 