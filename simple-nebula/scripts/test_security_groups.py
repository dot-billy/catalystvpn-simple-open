import requests
import json
from typing import Dict, Optional, List

BASE_URL = "http://myBackEndUrlOrIP:8000/api"

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
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def create_security_group(token: str, organization_slug: str, name: str, description: str = "") -> Optional[Dict]:
    """Create a security group."""
    try:
        data = {
            "name": name,
            "description": description,
            "firewall_rule_ids": [],
            "node_ids": [],
            "lighthouse_ids": []
        }
        url = f"{BASE_URL}/organizations/{organization_slug}/security-groups/"
        print(f"\nAttempting to create security group at URL: {url}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=data
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 201:
            print(f"Error response: {response.text}")
            response.raise_for_status()
            
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating security group: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def update_security_group(token: str, organization_slug: str, security_group_id: str, data: Dict) -> Optional[Dict]:
    """Update a security group."""
    try:
        response = requests.patch(
            f"{BASE_URL}/organizations/{organization_slug}/security-groups/{security_group_id}/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=data
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating security group: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def add_firewall_rule(token, organization_slug, security_group_id, rule_data):
    """Add a firewall rule to a security group."""
    url = f"{BASE_URL}/organizations/{organization_slug}/security-groups/{security_group_id}/add_rule/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\nAttempting to add firewall rule to security group at URL: {url}")
    print(f"Request data: {json.dumps(rule_data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=rule_data)
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 201:
        print("Successfully added firewall rule")
        return True
    else:
        print(f"Failed to add firewall rule: {response.text}")
        return False

def list_security_groups(token: str, organization_slug: str) -> Optional[List[Dict]]:
    """List all security groups for an organization."""
    try:
        url = f"{BASE_URL}/organizations/{organization_slug}/security-groups/"
        print(f"\nAttempting to list security groups at URL: {url}")
        
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            response.raise_for_status()
            
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error listing security groups: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def test_auth(token: str) -> bool:
    """Test authentication with a basic endpoint."""
    try:
        url = f"{BASE_URL}/organizations/"  # Using organizations endpoint for auth test
        print(f"\nTesting authentication with URL: {url}")
        
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            print("Authentication test successful!")
            return True
        else:
            print(f"Authentication test failed. Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error testing authentication: {e}")
        return False

def add_lighthouses_to_security_group(token: str, organization_slug: str, security_group_id: str, lighthouse_ids: List[str]) -> Optional[Dict]:
    """Add lighthouses to a security group."""
    try:
        # The endpoint expects just the lighthouse_ids in the request body
        data = {
            "lighthouse_ids": lighthouse_ids
        }
        url = f"{BASE_URL}/organizations/{organization_slug}/security-groups/{security_group_id}/add_lighthouses/"
        print(f"\nAttempting to add lighthouses to security group at URL: {url}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=data
        )
        
        print(f"Response status code: {response.status_code}")
        if response.status_code == 204:
            print("Successfully added lighthouses to security group")
            return {"status": "success"}
        elif response.status_code != 200:
            print(f"Error response: {response.text}")
            response.raise_for_status()
            
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding lighthouses to security group: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def add_nodes_to_security_group(token, organization_slug, security_group_id, node_ids):
    """Add nodes to a security group."""
    url = f"{BASE_URL}/organizations/{organization_slug}/security-groups/{security_group_id}/add_nodes/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'node_ids': node_ids
    }
    print(f"\nAttempting to add nodes to security group at URL: {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    response = requests.post(url, headers=headers, json=data)
    print(f"Response status code: {response.status_code}")
    if response.status_code == 204:
        print("Successfully added nodes to security group")
        return True
    elif response.status_code == 200:
        print("Successfully added nodes to security group")
        return True
    else:
        print(f"Error response: {response.text}")
        print(f"Error adding nodes to security group: {response.status_code} {response.reason}: {response.text}")
        return False

def get_lighthouses(token, organization_slug):
    """Get all lighthouses in an organization."""
    url = f"{BASE_URL}/organizations/{organization_slug}/lighthouses/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print(f"\nGetting lighthouses from URL: {url}")
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        lighthouses = response.json()
        print(f"Found {len(lighthouses)} lighthouses")
        return lighthouses
    else:
        print(f"Error response: {response.text}")
        print(f"Error getting lighthouses: {response.status_code} {response.reason}: {response.text}")
        return []

def get_security_group_by_name(token, organization_slug, name):
    """Get a security group by name."""
    url = f"{BASE_URL}/organizations/{organization_slug}/security-groups/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print(f"\nGetting security group by name from URL: {url}")
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        security_groups = response.json()
        for group in security_groups:
            if group['name'] == name:
                print(f"Found security group: {group['name']} (ID: {group['id']})")
                print(f"URL path: {url}{group['id']}/")
                return group['id']
        print(f"Security group '{name}' not found")
        return None
    else:
        print(f"Error response: {response.text}")
        print(f"Error getting security group: {response.status_code} {response.reason}: {response.text}")
        return None

def get_security_group_details(token, organization_slug, security_group_id):
    """Get detailed information about a security group."""
    url = f"{BASE_URL}/organizations/{organization_slug}/security-groups/{security_group_id}/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print(f"\nGetting security group details from URL: {url}")
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error response: {response.text}")
        print(f"Error getting security group details: {response.status_code} {response.reason}: {response.text}")
        return None

def main():
    # Admin credentials
    email = "myadminemail@gmail.com"
    password = "myAdminPassword"
    organization_slug = "deltaops"
    
    # Existing security group and node/lighthouse IDs
    existing_security_group_id = "0eb1341d-29ae-4432-b93b-11e2a2e8a01a"
    lighthouse_id = "88c3d7f7-cd6e-45c1-ae5c-42d0c830249f"
    node_id = "1f029ad5-419a-4218-a82c-51c96794a6eb"

    print("Attempting to authenticate...")
    # Get authentication token
    token = get_token(email, password)
    if not token:
        print("Failed to get authentication token")
        return

    print("Authentication successful!")
    print(f"Token: {token[:10]}...")

    # Test authentication with a basic endpoint
    if not test_auth(token):
        print("Failed basic authentication test. Please check server logs and API configuration.")
        return

    # Get the server_admins security group
    security_group_id = get_security_group_by_name(token, organization_slug, "server_admins")
    if not security_group_id:
        print("Security group 'server_admins' not found")
        return

    # Get all lighthouses in the organization
    lighthouses = get_lighthouses(token, organization_slug)
    if not lighthouses:
        print("No lighthouses found in the organization")
        return

    # Add all lighthouses to the security group
    lighthouse_ids = [lighthouse['id'] for lighthouse in lighthouses]
    print(f"\nAdding {len(lighthouse_ids)} lighthouses to security group")
    add_lighthouses_to_security_group(token, organization_slug, security_group_id, lighthouse_ids)

    # Add node to security group
    print("\nAdding node to security group...")
    add_nodes_to_security_group(token, organization_slug, security_group_id, [node_id])

    # Add SSH firewall rule
    ssh_rule = {
        "rule_type": "inbound",
        "protocol": "tcp",
        "port": "22",
        "cidr": "0.0.0.0/0"  # Allow SSH from anywhere
    }
    add_firewall_rule(token, organization_slug, security_group_id, ssh_rule)

    # Get and print security group details
    print("\nGetting security group details...")
    details = get_security_group_details(token, organization_slug, security_group_id)
    if details:
        print("\nSecurity Group Details:")
        print(json.dumps(details, indent=2))

    print("\nAll operations completed successfully!")

if __name__ == "__main__":
    main() 