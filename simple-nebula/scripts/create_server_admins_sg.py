import requests
import json
from typing import Dict, Optional, List

BASE_URL = "http://localhost:8000/api"

def get_token(email: str, password: str) -> Optional[str]:
    """Get JWT token by authenticating with email and password."""
    try:
        response = requests.post(
            f"{BASE_URL}/token/",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("access")
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_security_group(token: str, organization_slug: str, name: str) -> Optional[Dict]:
    """Get a security group by name."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/security-groups/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        security_groups = response.json()
        for group in security_groups:
            if group["name"] == name:
                return group
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting security group: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def create_security_group(token: str, organization_slug: str, name: str, description: str = "") -> Optional[Dict]:
    """Create a security group."""
    try:
        # First check if the security group already exists
        existing_group = get_security_group(token, organization_slug, name)
        if existing_group:
            print(f"Security group '{name}' already exists. Using existing group.")
            return existing_group

        # First get the organization ID from the slug
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        organization = response.json()
        organization_id = organization["id"]

        # Now create the security group with the organization ID
        data = {
            "name": name,
            "description": description,
            "organization": organization_id
        }
        response = requests.post(
            f"{BASE_URL}/organizations/{organization_slug}/security-groups/",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating security group: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def add_firewall_rules(security_group_id, token):
    """Add firewall rules to the security group."""
    # Add rules for each node to allow SSH from network_admins group
    rules = [
        # Allow SSH from network_admins group
        {
            "rule_type": "inbound",
            "protocol": "tcp",
            "port": "22",
            "group": "network_admins"  # Reference by name
        },
        # Allow all outbound traffic
        {
            "rule_type": "outbound",
            "protocol": "any",
            "port": "any",
            "cidr": "0.0.0.0/0"
        },
        # Allow ICMP (ping) from any host
        {
            "rule_type": "inbound",
            "protocol": "icmp",
            "port": None,
            "cidr": "0.0.0.0/0"
        }
    ]

    for rule in rules:
        response = requests.post(
            f"{BASE_URL}/security-groups/{security_group_id}/add_rule/",
            headers={"Authorization": f"Bearer {token}"},
            json=rule
        )
        if response.status_code not in [200, 201, 204]:
            print(f"Error adding rule {rule}: {response.status_code} - {response.text}")
            return False
        print(f"Added rule: {rule}")

    return True

def add_nodes_to_security_group(token: str, organization_slug: str, security_group_id: str, node_ids: List[str]) -> bool:
    """Add nodes to a security group."""
    try:
        print(f"\nAttempting to add nodes to security group {security_group_id}")
        print(f"Node IDs: {node_ids}")
        
        # First get the organization ID from the slug
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        organization = response.json()
        organization_id = organization["id"]
        print(f"Organization ID: {organization_id}")

        # Update the security group with the node IDs
        url = f"{BASE_URL}/organizations/{organization_slug}/security-groups/{security_group_id}/"
        print(f"Making request to: {url}")
        
        # Use the correct request format for updating the security group
        data = {
            "node_ids": node_ids
        }
        print(f"Request payload: {data}")
        
        response = requests.patch(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")
        
        if response.status_code in [200, 201, 204]:
            print("Successfully added nodes to security group")
            return True
            
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error adding nodes to security group: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def verify_nodes(token: str, organization_slug: str, node_ids: List[str]) -> bool:
    """Verify that all nodes exist in the organization."""
    try:
        # First get the organization ID from the slug
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        organization = response.json()
        organization_id = organization["id"]

        # Now get the nodes using the organization ID
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_id}/nodes/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        nodes = response.json()
        print(f"Found {len(nodes)} nodes in organization {organization_slug}:")
        for node in nodes:
            print(f"  - {node['name']} (ID: {node['id']})")
        existing_node_ids = {node["id"] for node in nodes}
        missing_nodes = set(node_ids) - existing_node_ids
        if missing_nodes:
            print(f"Error: The following nodes do not exist in the organization: {missing_nodes}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error verifying nodes: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def main():
    # Replace these with your actual credentials and organization
    email = "myadminemail@gmail.com"  # Admin user with operator role
    password = "p2440wrd"  # Admin password
    organization_slug = "deltaops"
    
    # Using five random nodes from the list
    node_ids = [
        "88c3d7f7-cd6e-45c1-ae5c-42d0c830249f",  # Test Node 
        "bc5dc769-8645-43c4-9b4d-a0fdc17aa245",  # Test Node-1
        "a6cec648-2e3a-4701-9047-52f49974a0ab",  # Test Node-10
        "d6d89662-e131-4ce3-8416-cf8259b8322b",  # Test Node-11
        "7c6b198b-fa13-425a-9659-81d8cdef79bf"   # Test Node-12
    ]
    
    # Replace this with the actual UUID of the network_admins security group
    network_admins_group_id = "network-admins-uuid"

    # Get authentication token
    token = get_token(email, password)
    if not token:
        print("Failed to get authentication token")
        return

    # Verify nodes exist in the organization
    if not verify_nodes(token, organization_slug, node_ids):
        print("Failed to verify nodes")
        return

    # Create the server_admins security group
    server_admins = create_security_group(
        token=token,
        organization_slug=organization_slug,
        name="server_admins",
        description="Security group for server administrators with SSH access"
    )
    if not server_admins:
        print("Failed to create server_admins security group")
        return

    print(f"Created server_admins security group: {json.dumps(server_admins, indent=2)}")

    # Add the nodes to the security group
    if not add_nodes_to_security_group(token, organization_slug, server_admins["id"], node_ids):
        print("Failed to add nodes to security group")
        return

    # Add firewall rules
    if not add_firewall_rules(server_admins["id"], token):
        print("Failed to add firewall rules")
        return

    print("Successfully created server_admins security group with Nebula-style firewall rules!")

if __name__ == "__main__":
    main() 