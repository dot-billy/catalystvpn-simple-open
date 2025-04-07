# Nodes and Lighthouses

This document describes how to manage nodes and lighthouses in Simple Nebula.

## Overview

In Nebula:
- **Nodes** are regular devices in the mesh network
- **Lighthouses** are special nodes that help with NAT traversal and discovery

## Node Model

Nodes represent devices in your Nebula mesh network:

- **ID**: UUID primary key
- **Organization**: The organization this node belongs to
- **Network**: The network this node is part of
- **Name**: Human-readable name
- **Hostname**: DNS hostname or IP address
- **Nebula IP**: IP address within the Nebula network
- **Certificate**: X.509 certificate for the node
- **Lighthouse**: Optional reference to a lighthouse that this node connects to
- **Security Groups**: Associated security groups
- **Last Check-in**: Timestamp of the last check-in
- **Config**: JSON configuration data
- **Created/Updated At**: Timestamps

## Lighthouse Model

Lighthouses are special nodes that help with NAT traversal and discovery:

- **ID**: UUID primary key
- **Organization**: The organization this lighthouse belongs to
- **Network**: The network this lighthouse is part of
- **Name**: Human-readable name
- **Hostname**: DNS hostname or IP address
- **Nebula IP**: IP address within the Nebula network
- **Public IP**: Public IP address or hostname
- **Port**: Port number (default: 4242)
- **Is Active**: Boolean indicating if the lighthouse is active
- **Certificate**: X.509 certificate for the lighthouse
- **Security Groups**: Associated security groups
- **Last Check-in**: Timestamp of the last check-in
- **Config**: JSON configuration data
- **Created/Updated At**: Timestamps

## Managing Nodes

### Listing Nodes

To list all nodes in an organization:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/nodes/" \
  -H "Authorization: Bearer <access_token>"
```

### Creating Nodes

To create a new node:

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/nodes/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Web Server 1",
    "hostname": "webserver1.example.com",
    "network_id": "<network-id>",
    "lighthouse_id": "<lighthouse-id>",
    "security_group_ids": ["<security-group-id-1>", "<security-group-id-2>"]
  }'
```

Notes:
- If `network_id` is not provided, the node will be assigned to the organization's primary network
- If `nebula_ip` is not provided, one will be automatically assigned from the network
- If `lighthouse_id` is not provided, the node will not be associated with a lighthouse

### Node Details

To get details about a specific node:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/nodes/<node-id>/" \
  -H "Authorization: Bearer <access_token>"
```

### Updating Nodes

To update a node:

```bash
curl -X PATCH "http://localhost:8000/api/organizations/<slug>/nodes/<node-id>/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Node Name",
    "hostname": "updated-hostname.example.com",
    "lighthouse_id": "<new-lighthouse-id>"
  }'
```

### Deleting Nodes

To delete a node:

```bash
curl -X DELETE "http://localhost:8000/api/organizations/<slug>/nodes/<node-id>/" \
  -H "Authorization: Bearer <access_token>"
```

### Getting Node Configuration

To get the Nebula configuration for a node:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/nodes/<node-id>/config/" \
  -H "Authorization: Bearer <access_token>"
```

## Managing Lighthouses

### Listing Lighthouses

To list all lighthouses in an organization:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/lighthouses/" \
  -H "Authorization: Bearer <access_token>"
```

### Creating Lighthouses

To create a new lighthouse:

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/lighthouses/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Primary Lighthouse",
    "hostname": "lighthouse.example.com",
    "public_ip": "203.0.113.10",
    "port": 4242,
    "network_id": "<network-id>",
    "security_group_ids": ["<security-group-id-1>", "<security-group-id-2>"]
  }'
```

Notes:
- If `network_id` is not provided, the lighthouse will be assigned to the organization's primary network
- If `nebula_ip` is not provided, one will be automatically assigned from the network
- `public_ip` is required and must be reachable by other nodes
- `port` defaults to 4242 if not specified

### Lighthouse Details

To get details about a specific lighthouse:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/lighthouses/<lighthouse-id>/" \
  -H "Authorization: Bearer <access_token>"
```

### Updating Lighthouses

To update a lighthouse:

```bash
curl -X PATCH "http://localhost:8000/api/organizations/<slug>/lighthouses/<lighthouse-id>/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Lighthouse Name",
    "public_ip": "203.0.113.20",
    "is_active": true
  }'
```

### Deleting Lighthouses

To delete a lighthouse:

```bash
curl -X DELETE "http://localhost:8000/api/organizations/<slug>/lighthouses/<lighthouse-id>/" \
  -H "Authorization: Bearer <access_token>"
```

Note: Lighthouses with associated nodes cannot be deleted unless those nodes are first reassigned or deleted.

### Getting Lighthouse Configuration

To get the Nebula configuration for a lighthouse:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/lighthouses/<lighthouse-id>/config/" \
  -H "Authorization: Bearer <access_token>"
```

## Certificates

Both nodes and lighthouses require certificates to participate in the Nebula network. Certificates are automatically generated when nodes and lighthouses are created.

To get the certificate for a node or lighthouse:

```bash
# For nodes
curl -X GET "http://localhost:8000/api/organizations/<slug>/nodes/<node-id>/certificate/" \
  -H "Authorization: Bearer <access_token>"

# For lighthouses
curl -X GET "http://localhost:8000/api/organizations/<slug>/lighthouses/<lighthouse-id>/certificate/" \
  -H "Authorization: Bearer <access_token>"
```

## API Endpoints

### Node Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/organizations/<slug>/nodes/` | GET | List nodes |
| `/api/organizations/<slug>/nodes/` | POST | Create a node |
| `/api/organizations/<slug>/nodes/<id>/` | GET | Get node details |
| `/api/organizations/<slug>/nodes/<id>/` | PATCH | Update node |
| `/api/organizations/<slug>/nodes/<id>/` | DELETE | Delete node |
| `/api/organizations/<slug>/nodes/<id>/config/` | GET | Get node configuration |
| `/api/organizations/<slug>/nodes/<id>/certificate/` | GET | Get node certificate |

### Lighthouse Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/organizations/<slug>/lighthouses/` | GET | List lighthouses |
| `/api/organizations/<slug>/lighthouses/` | POST | Create a lighthouse |
| `/api/organizations/<slug>/lighthouses/<id>/` | GET | Get lighthouse details |
| `/api/organizations/<slug>/lighthouses/<id>/` | PATCH | Update lighthouse |
| `/api/organizations/<slug>/lighthouses/<id>/` | DELETE | Delete lighthouse |
| `/api/organizations/<slug>/lighthouses/<id>/config/` | GET | Get lighthouse configuration |
| `/api/organizations/<slug>/lighthouses/<id>/certificate/` | GET | Get lighthouse certificate | 