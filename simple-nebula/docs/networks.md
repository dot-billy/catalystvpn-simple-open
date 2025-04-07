# Networks

This document describes how to manage networks in Simple Nebula.

## Network Model

Networks define IP address spaces using CIDR notation. Each organization can have multiple networks, with one designated as the primary network. The primary network is created automatically when an organization is created.

Network properties:
- **ID**: UUID primary key
- **Organization**: The organization this network belongs to
- **Name**: Human-readable name
- **CIDR**: IP range in CIDR notation (e.g., "10.0.0.0/16")
- **Description**: Optional description
- **Is Primary**: Boolean indicating if this is the primary network
- **Created/Updated At**: Timestamps

## Primary Networks

Each organization has exactly one primary network, which is created automatically when the organization is created. The primary network:
- Is used as the default for new nodes and lighthouses
- Is associated with the organization's certificate authority
- Cannot be deleted (unless the organization is deleted)

## Listing Networks

To list all networks in an organization:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/networks/" \
  -H "Authorization: Bearer <access_token>"
```

## Creating Networks

Organization admins and operators can create additional networks:

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/networks/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Secondary Network",
    "cidr": "10.20.0.0/16",
    "description": "A secondary network for development"
  }'
```

## Retrieving Network Details

To get details about a specific network:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/networks/<network-id>/" \
  -H "Authorization: Bearer <access_token>"
```

## Updating Networks

Organization admins and operators can update network details:

```bash
curl -X PATCH "http://localhost:8000/api/organizations/<slug>/networks/<network-id>/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Network Name",
    "description": "Updated description"
  }'
```

Note: Changing the CIDR of a network with existing nodes/lighthouses is not allowed.

## Deleting Networks

Organization admins and operators can delete non-primary networks:

```bash
curl -X DELETE "http://localhost:8000/api/organizations/<slug>/networks/<network-id>/" \
  -H "Authorization: Bearer <access_token>"
```

Note: Networks with associated nodes or lighthouses cannot be deleted.

## Available IPs

To get the next available IP address from a network:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/networks/<network-id>/available_ips/" \
  -H "Authorization: Bearer <access_token>"
```

## IP Management

Networks automatically manage IP addresses for nodes and lighthouses:

1. When a node or lighthouse is created without a specified IP, the system automatically assigns the next available IP from the network.
2. The system tracks used IPs to avoid conflicts.
3. IPs are verified to be within the network's CIDR range.

## Node and Lighthouse Assignment

Nodes and lighthouses must be assigned to a network. By default, they are assigned to the organization's primary network, but they can be explicitly assigned to any network within the organization.

When creating a node or lighthouse, you can specify the network:

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/nodes/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Node",
    "hostname": "mynode.example.com",
    "network_id": "<network-id>"
  }'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/organizations/<slug>/networks/` | GET | List networks |
| `/api/organizations/<slug>/networks/` | POST | Create a network |
| `/api/organizations/<slug>/networks/<id>/` | GET | Get network details |
| `/api/organizations/<slug>/networks/<id>/` | PATCH | Update network |
| `/api/organizations/<slug>/networks/<id>/` | DELETE | Delete network |
| `/api/organizations/<slug>/networks/<id>/available_ips/` | GET | Get next available IP | 