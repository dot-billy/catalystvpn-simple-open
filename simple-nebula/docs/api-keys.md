# API Keys

This document describes how to manage API keys in Simple Nebula.

## Overview

API keys provide an alternative authentication method for automated access to the API. They are especially useful for:

- Node and lighthouse access
- Automation scripts
- Integration with other systems

## API Key Model

API keys have the following properties:

- **ID**: UUID primary key
- **Name**: Human-readable name
- **Key Hash**: Hashed version of the API key (the actual key is only displayed once when created)
- **Entity Type**: Type of entity the key is associated with (node, lighthouse)
- **Node ID**: Foreign key to a node (if entity_type is "node")
- **Lighthouse ID**: Foreign key to a lighthouse (if entity_type is "lighthouse")
- **Created At**: Creation timestamp
- **Expires At**: Optional expiration timestamp
- **Last Used**: Timestamp of last usage
- **Is Active**: Boolean indicating if the key is active

## Managing API Keys

### Listing API Keys

To list all API keys in an organization:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/api-keys/" \
  -H "Authorization: Bearer <access_token>"
```

### Creating API Keys

To create a new API key for a node:

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/api-keys/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Node API Key",
    "entity_type": "node",
    "node_id": "<node-id>",
    "expires_at": "2025-12-31T23:59:59Z"
  }'
```

To create a new API key for a lighthouse:

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/api-keys/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lighthouse API Key",
    "entity_type": "lighthouse",
    "lighthouse_id": "<lighthouse-id>",
    "expires_at": "2025-12-31T23:59:59Z"
  }'
```

Notes:
- The `expires_at` field is optional. If not provided, the API key will not expire.
- When an API key is created, the response will include the full API key. This is the only time the full key will be displayed. Store it securely.

Example response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Node API Key",
  "entity_type": "node",
  "node": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Web Server 1"
  },
  "created_at": "2023-04-01T12:00:00Z",
  "expires_at": "2025-12-31T23:59:59Z",
  "is_active": true,
  "key": "nebula_ak_550e8400e29b41d4a716446655440000"  // This is only shown once!
}
```

### API Key Details

To get details about a specific API key:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/api-keys/<api-key-id>/" \
  -H "Authorization: Bearer <access_token>"
```

Note: The API key itself is not included in the response.

### Updating API Keys

To update an API key (only the name and active status can be updated):

```bash
curl -X PATCH "http://localhost:8000/api/organizations/<slug>/api-keys/<api-key-id>/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated API Key Name",
    "is_active": false
  }'
```

### Deleting API Keys

To delete an API key:

```bash
curl -X DELETE "http://localhost:8000/api/organizations/<slug>/api-keys/<api-key-id>/" \
  -H "Authorization: Bearer <access_token>"
```

## Using API Keys

To use an API key for authentication, include it in the Authorization header:

```
Authorization: Api-Key nebula_ak_550e8400e29b41d4a716446655440000
```

For example:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/nodes/<node-id>/" \
  -H "Authorization: Api-Key nebula_ak_550e8400e29b41d4a716446655440000"
```

### Access Control

API keys have specific access control:

1. **Node API Keys**:
   - Can only access the specific node they are associated with
   - Can update node properties and retrieve node configuration
   - Cannot create or delete nodes
   - Cannot access other organization resources

2. **Lighthouse API Keys**:
   - Can only access the specific lighthouse they are associated with
   - Can update lighthouse properties and retrieve lighthouse configuration
   - Cannot create or delete lighthouses
   - Cannot access other organization resources

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/organizations/<slug>/api-keys/` | GET | List API keys |
| `/api/organizations/<slug>/api-keys/` | POST | Create an API key |
| `/api/organizations/<slug>/api-keys/<id>/` | GET | Get API key details |
| `/api/organizations/<slug>/api-keys/<id>/` | PATCH | Update an API key |
| `/api/organizations/<slug>/api-keys/<id>/` | DELETE | Delete an API key | 