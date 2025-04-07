# Organization Management

This document describes how to manage organizations in Simple Nebula.

## Organization Model

Organizations are the top-level containers for resources in Simple Nebula. Each organization has:

- A unique ID (UUID)
- A human-readable name
- A URL-friendly slug (automatically generated from the name)
- An optional description
- A list of member users (with roles)
- A primary network (created automatically with the organization)
- A certificate authority (created automatically with the organization)

## Creating an Organization

To create a new organization, make a POST request to the `/api/organizations/` endpoint:

```bash
curl -X POST "http://localhost:8000/api/organizations/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Organization",
    "description": "My organization description",
    "cidr": "10.10.0.0/16"
  }'
```

When an organization is created:

1. The user who created it automatically becomes an admin member
2. A primary network is created with the specified CIDR (or a default if not provided)
3. A certificate authority (CA) is created for the organization

## Organization List and Details

To list organizations the current user has access to:

```bash
curl -X GET "http://localhost:8000/api/organizations/" \
  -H "Authorization: Bearer <access_token>"
```

To get details about a specific organization:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/" \
  -H "Authorization: Bearer <access_token>"
```

## Updating an Organization

Organization admins can update organization details:

```bash
curl -X PATCH "http://localhost:8000/api/organizations/<slug>/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Organization Name",
    "description": "Updated description"
  }'
```

## Deleting an Organization

Organization admins can delete an organization:

```bash
curl -X DELETE "http://localhost:8000/api/organizations/<slug>/" \
  -H "Authorization: Bearer <access_token>"
```

Deleting an organization will delete all associated resources, including:
- Networks
- Security groups
- Nodes
- Lighthouses
- Certificates
- Memberships

## Managing Organization Members

Please refer to the [User Management documentation](./user-management.md#managing-roles-and-permissions) for details on managing organization members and roles.

### List Organization Members

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/members/" \
  -H "Authorization: Bearer <access_token>"
```

### Add Member to Organization

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/members/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<user-uuid>",
    "role": "viewer"
  }'
```

### Update Member Role

```bash
curl -X PATCH "http://localhost:8000/api/organizations/<slug>/members/<membership-id>/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "operator"
  }'
```

### Remove Member from Organization

```bash
curl -X DELETE "http://localhost:8000/api/organizations/<slug>/members/<membership-id>/" \
  -H "Authorization: Bearer <access_token>"
```

## Organization Resources

Each organization acts as a container for various resources:

- **Networks**: IP address ranges for the organization's nodes
- **Security Groups**: Firewall rule containers
- **Nodes**: End devices in the Nebula network
- **Lighthouses**: Special nodes that help with NAT traversal and discovery
- **Certificates**: X.509 certificates for nodes and lighthouses

All these resources are accessible through nested endpoints under the organization:

```
/api/organizations/<slug>/networks/
/api/organizations/<slug>/security-groups/
/api/organizations/<slug>/nodes/
/api/organizations/<slug>/lighthouses/
/api/organizations/<slug>/certificates/
```

## Certificate Authority

Each organization has its own Certificate Authority (CA) that's created automatically when the organization is created. The CA is used to issue certificates for nodes and lighthouses.

### Get CA Information

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/ca/" \
  -H "Authorization: Bearer <access_token>"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/organizations/` | GET | List organizations the user has access to |
| `/api/organizations/` | POST | Create a new organization |
| `/api/organizations/<slug>/` | GET | Get organization details |
| `/api/organizations/<slug>/` | PATCH | Update organization |
| `/api/organizations/<slug>/` | DELETE | Delete organization |
| `/api/organizations/<slug>/members/` | GET | List organization members |
| `/api/organizations/<slug>/members/` | POST | Add member to organization |
| `/api/organizations/<slug>/members/<uuid>/` | PATCH | Update member role |
| `/api/organizations/<slug>/members/<uuid>/` | DELETE | Remove member from organization |
| `/api/organizations/<slug>/ca/` | GET | Get organization's certificate authority | 