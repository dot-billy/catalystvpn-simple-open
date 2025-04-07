import requests
import json
import sys
from typing import Dict, Optional, List
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

def get_token(email: str, password: str) -> Optional[str]:
    """Get JWT token by authenticating with email and password."""
    try:
        response = requests.post(
            f"{BASE_URL}/token/",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        return response.json()["access"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_organizations(token: str) -> Optional[List[Dict]]:
    """Get organizations the user is a member of."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting organizations: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_primary_network(token: str, organization_slug: str) -> Optional[Dict]:
    """Get the primary network for an organization."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/networks/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        networks = response.json()
        # Find the primary network
        for network in networks:
            if network.get('is_primary'):
                return network
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting organization network: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_ca(token: str, organization_slug: str) -> Optional[Dict]:
    """Get the certificate authority for an organization."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/ca/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting CA: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_security_groups(token: str, organization_slug: str) -> Optional[List[Dict]]:
    """Get security groups for an organization."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/security-groups/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting security groups: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_lighthouses(token: str, organization_slug: str) -> Optional[List[Dict]]:
    """Get lighthouses for an organization."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/lighthouses/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting lighthouses: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_nodes(token: str, organization_slug: str) -> Optional[List[Dict]]:
    """Get nodes for an organization."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/nodes/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting nodes: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def create_primary_network(token: str, organization_slug: str) -> Optional[Dict]:
    """Create a primary network for an organization."""
    try:
        response = requests.post(
            f"{BASE_URL}/organizations/{organization_slug}/networks/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Primary Network",
                "cidr": "192.168.100.0/24",
                "description": "Primary network for organization",
                "is_primary": True
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating primary network: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def create_ca(token: str, organization_slug: str, network_id: str) -> Optional[Dict]:
    """Create a certificate authority for an organization."""
    try:
        # Calculate expiration date (1 year from now)
        expires_at = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        response = requests.post(
            f"{BASE_URL}/organizations/{organization_slug}/ca/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "network": network_id,
                "expires_at": expires_at
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating CA: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def create_security_group(token: str, organization_slug: str) -> Optional[Dict]:
    """Create a security group for an organization."""
    try:
        response = requests.post(
            f"{BASE_URL}/organizations/{organization_slug}/security-groups/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "default",
                "description": "Default security group"
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating security group: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def create_lighthouse(token: str, organization_slug: str, network_id: str) -> Optional[Dict]:
    """Create a lighthouse for an organization."""
    try:
        response = requests.post(
            f"{BASE_URL}/organizations/{organization_slug}/lighthouses/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "test-lighthouse",
                "hostname": "test-lighthouse.example.com",
                "public_ip": "1.2.3.4",
                "port": 4242,
                "network": network_id
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating lighthouse: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def create_node(token: str, organization_slug: str, network_id: str) -> Optional[Dict]:
    """Create a node for an organization."""
    try:
        response = requests.post(
            f"{BASE_URL}/organizations/{organization_slug}/nodes/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "test-node",
                "hostname": "test-node.example.com",
                "network": network_id
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating node: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python check_organization.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    print(f"\nTesting authentication for {email}...")
    
    # Step 1: Get JWT token
    token = get_token(email, password)
    if not token:
        print("Failed to get token. Exiting.")
        sys.exit(1)
    print("Successfully obtained token!")

    # Step 2: Get organizations
    organizations = get_organizations(token)
    if not organizations:
        print("No organizations found or error retrieving organizations.")
        sys.exit(1)

    print("\nChecking organizations:")
    for org in organizations:
        org_slug = org['slug']
        print(f"\nOrganization: {org['name']} ({org_slug})")
        
        # Check primary network
        print("\n1. Checking primary network...")
        primary_network = get_primary_network(token, org_slug)
        if primary_network:
            print(f"✓ Found primary network: {primary_network['name']} ({primary_network['cidr']})")
        else:
            print("✗ No primary network found. Creating one...")
            primary_network = create_primary_network(token, org_slug)
            if primary_network:
                print(f"✓ Created primary network: {primary_network['name']} ({primary_network['cidr']})")
            else:
                print("✗ Failed to create primary network. Skipping organization.")
                continue

        # Check CA
        print("\n2. Checking certificate authority...")
        ca = get_ca(token, org_slug)
        if ca:
            print(f"✓ Found CA (expires: {ca['expires_at']})")
        else:
            print("✗ No CA found. Creating one...")
            ca = create_ca(token, org_slug, primary_network['id'])
            if ca:
                print(f"✓ Created CA (expires: {ca['expires_at']})")
            else:
                print("✗ Failed to create CA. Skipping organization.")
                continue

        # Check security groups
        print("\n3. Checking security groups...")
        security_groups = get_security_groups(token, org_slug)
        if security_groups and len(security_groups) > 0:
            print(f"✓ Found {len(security_groups)} security groups")
        else:
            print("✗ No security groups found. Creating one...")
            security_group = create_security_group(token, org_slug)
            if security_group:
                print(f"✓ Created security group: {security_group['name']}")
            else:
                print("✗ Failed to create security group. Skipping organization.")
                continue

        # Check lighthouses
        print("\n4. Checking lighthouses...")
        lighthouses = get_lighthouses(token, org_slug)
        if lighthouses and len(lighthouses) > 0:
            print(f"✓ Found {len(lighthouses)} lighthouses")
        else:
            print("✗ No lighthouses found. Creating one...")
            lighthouse = create_lighthouse(token, org_slug, primary_network['id'])
            if lighthouse:
                print(f"✓ Created lighthouse: {lighthouse['name']}")
            else:
                print("✗ Failed to create lighthouse. Skipping organization.")
                continue

        # Check nodes
        print("\n5. Checking nodes...")
        nodes = get_nodes(token, org_slug)
        if nodes and len(nodes) > 0:
            print(f"✓ Found {len(nodes)} nodes")
        else:
            print("✗ No nodes found. Creating one...")
            node = create_node(token, org_slug, primary_network['id'])
            if node:
                print(f"✓ Created node: {node['name']}")
            else:
                print("✗ Failed to create node. Skipping organization.")
                continue

if __name__ == "__main__":
    main() 