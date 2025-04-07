# Security Groups

This document describes how to manage security groups and firewall rules in Simple Nebula.

## Security Group Model

Security groups are collections of firewall rules that can be applied to nodes and lighthouses. They function similarly to AWS security groups, allowing you to define access control for your Nebula network.

Security group properties:
- **ID**: UUID primary key
- **Organization**: The organization this security group belongs to
- **Name**: Human-readable name
- **Description**: Optional description
- **Created/Updated At**: Timestamps

## Firewall Rule Model

Firewall rules define access control policies within security groups. Each rule specifies:

- **Rule Type**: Inbound or outbound
- **Protocol**: TCP, UDP, ICMP, or any
- **Port**: Port number, port range, or "any"
- **Source/Destination**: Can be one of:
  - CIDR notation (e.g., "0.0.0.0/0" for anywhere)
  - Host name or IP address
  - Another security group

## Listing Security Groups

To list all security groups in an organization:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/security-groups/" \
  -H "Authorization: Bearer <access_token>"
```

## Creating Security Groups

Organization admins and operators can create security groups:

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/security-groups/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Web Servers",
    "description": "Security group for web servers"
  }'
```

## Retrieving Security Group Details

To get details about a specific security group:

```bash
curl -X GET "http://localhost:8000/api/organizations/<slug>/security-groups/<security-group-id>/" \
  -H "Authorization: Bearer <access_token>"
```

## Updating Security Groups

Organization admins and operators can update security group details:

```bash
curl -X PATCH "http://localhost:8000/api/organizations/<slug>/security-groups/<security-group-id>/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Security Group Name",
    "description": "Updated description"
  }'
```

## Deleting Security Groups

Organization admins and operators can delete security groups:

```bash
curl -X DELETE "http://localhost:8000/api/organizations/<slug>/security-groups/<security-group-id>/" \
  -H "Authorization: Bearer <access_token>"
```

Note: Security groups that are referenced by other security groups cannot be deleted.

## Managing Firewall Rules

### Adding Rules

To add a firewall rule to a security group:

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/security-groups/<security-group-id>/add_rule/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_type": "inbound",
    "protocol": "tcp",
    "port": "80",
    "cidr": "0.0.0.0/0"
  }'
```

#### Example Rules

Allow inbound SSH from anywhere:
```json
{
  "rule_type": "inbound",
  "protocol": "tcp",
  "port": "22",
  "cidr": "0.0.0.0/0"
}
```

Allow inbound HTTP and HTTPS:
```json
{
  "rule_type": "inbound",
  "protocol": "tcp",
  "port": "80,443",
  "cidr": "0.0.0.0/0"
}
```

Allow a port range:
```json
{
  "rule_type": "inbound",
  "protocol": "tcp",
  "port": "8000-9000",
  "cidr": "10.10.0.0/16"
}
```

Allow access from another security group:
```json
{
  "rule_type": "inbound",
  "protocol": "tcp",
  "port": "3306",
  "group": "<security-group-id>"
}
```

Allow all ICMP:
```json
{
  "rule_type": "inbound",
  "protocol": "icmp",
  "cidr": "0.0.0.0/0"
}
```

### Deleting Rules

To delete a firewall rule:

```bash
curl -X DELETE "http://localhost:8000/api/organizations/<slug>/security-groups/<security-group-id>/rules/<rule-id>/" \
  -H "Authorization: Bearer <access_token>"
```

## Assigning Security Groups to Nodes and Lighthouses

### Adding Nodes to a Security Group

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/security-groups/<security-group-id>/add_nodes/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "node_ids": ["<node-id-1>", "<node-id-2>"]
  }'
```

### Adding Lighthouses to a Security Group

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/security-groups/<security-group-id>/add_lighthouses/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lighthouse_ids": ["<lighthouse-id-1>", "<lighthouse-id-2>"]
  }'
```

### Removing Nodes from a Security Group

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/security-groups/<security-group-id>/remove_nodes/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "node_ids": ["<node-id-1>", "<node-id-2>"]
  }'
```

### Removing Lighthouses from a Security Group

```bash
curl -X POST "http://localhost:8000/api/organizations/<slug>/security-groups/<security-group-id>/remove_lighthouses/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lighthouse_ids": ["<lighthouse-id-1>", "<lighthouse-id-2>"]
  }'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/organizations/<slug>/security-groups/` | GET | List security groups |
| `/api/organizations/<slug>/security-groups/` | POST | Create a security group |
| `/api/organizations/<slug>/security-groups/<id>/` | GET | Get security group details |
| `/api/organizations/<slug>/security-groups/<id>/` | PATCH | Update security group |
| `/api/organizations/<slug>/security-groups/<id>/` | DELETE | Delete security group |
| `/api/organizations/<slug>/security-groups/<id>/add_rule/` | POST | Add a firewall rule |
| `/api/organizations/<slug>/security-groups/<id>/rules/<rule_id>/` | DELETE | Delete a firewall rule |
| `/api/organizations/<slug>/security-groups/<id>/add_nodes/` | POST | Add nodes to the security group |
| `/api/organizations/<slug>/security-groups/<id>/add_lighthouses/` | POST | Add lighthouses to the security group |
| `/api/organizations/<slug>/security-groups/<id>/remove_nodes/` | POST | Remove nodes from the security group |
| `/api/organizations/<slug>/security-groups/<id>/remove_lighthouses/` | POST | Remove lighthouses from the security group | 