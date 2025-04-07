import requests
import json
import sys
from typing import Dict, Optional

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

def get_user_info(token: str) -> Optional[Dict]:
    """Get user information using the JWT token."""
    try:
        response = requests.get(
            f"{BASE_URL}/users/me/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting user info: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_organizations(token: str) -> Optional[Dict]:
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

def get_organization_memberships(token: str, organization_slug: str) -> Optional[Dict]:
    """Get user's membership in a specific organization."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/members/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting organization memberships: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_security_groups(token: str, organization_slug: str) -> Optional[Dict]:
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

def get_lighthouses(token: str, organization_slug: str) -> Optional[Dict]:
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

def check_user_roles(token: str) -> Optional[Dict]:
    """Check user roles and permissions."""
    try:
        response = requests.get(
            f"{BASE_URL}/users/me/",  # Changed to use the user info endpoint
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        user_data = response.json()
        return {
            "is_admin": user_data.get("is_superuser", False),
            "is_operator": user_data.get("is_staff", False)
        }
    except requests.exceptions.RequestException as e:
        print(f"Error checking user roles: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def find_org_without_security_groups(token: str) -> Optional[Dict]:
    """Find an organization that has no security groups."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        organizations = response.json()
        
        for org in organizations:
            org_slug = org['slug']
            # Check if org has any security groups
            sg_response = requests.get(
                f"{BASE_URL}/organizations/{org_slug}/security-groups/",
                headers={"Authorization": f"Bearer {token}"}
            )
            if sg_response.status_code == 200 and len(sg_response.json()) == 0:
                return org
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error finding organization: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def create_security_group(token: str, organization_slug: str) -> Optional[Dict]:
    """Create a security group in an organization."""
    try:
        data = {
            "name": "test-security-group",
            "description": "Test security group created via API"
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
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def find_org_without_lighthouses(token: str) -> Optional[Dict]:
    """Find an organization that has no lighthouses."""
    try:
        response = requests.get(
            f"{BASE_URL}/organizations/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        organizations = response.json()
        
        for org in organizations:
            org_slug = org['slug']
            # Check if org has any lighthouses
            lh_response = requests.get(
                f"{BASE_URL}/organizations/{org_slug}/lighthouses/",
                headers={"Authorization": f"Bearer {token}"}
            )
            if lh_response.status_code == 200 and len(lh_response.json()) == 0:
                return org
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error finding organization: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_organization_network(token: str, organization_slug: str) -> Optional[Dict]:
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

def create_lighthouse(token: str, organization_slug: str) -> Optional[Dict]:
    """Create a lighthouse in an organization."""
    try:
        # Get the primary network for the organization
        network = get_organization_network(token, organization_slug)
        if not network:
            print("No primary network found for organization")
            return None

        data = {
            "name": "test-lighthouse",
            "hostname": "test-lighthouse.example.com",
            "description": "Test lighthouse created via API",
            "public_ip": "1.2.3.4",  # Example public IP
            "network": str(network['id']),  # Convert UUID to string
            "port": 4242  # Default Nebula port
        }
        print(f"Creating lighthouse with data: {data}")  # Debug print
        response = requests.post(
            f"{BASE_URL}/organizations/{organization_slug}/lighthouses/",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating lighthouse: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python test_auth.py <email> <password>")
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

    # Step 2: Get user info and check roles
    user_info = get_user_info(token)
    if not user_info:
        print("Failed to get user info. Exiting.")
        sys.exit(1)
    print("\nUser Info:")
    print(json.dumps(user_info, indent=2))

    # Check roles from user info
    is_admin = user_info.get("is_superuser", False)
    is_operator = user_info.get("is_staff", False)
    
    if is_admin:
        print("\n✅ User has ADMIN role (is_superuser)")
    if is_operator:
        print("\n✅ User has OPERATOR role (is_staff)")
    if not (is_admin or is_operator):
        print("\n❌ User does not have ADMIN or OPERATOR role")

    # Step 3: Get organizations
    organizations = get_organizations(token)
    if organizations:
        print("\nOrganizations:")
        print(json.dumps(organizations, indent=2))
        
        # Step 4: Get memberships, security groups, and lighthouses for each organization
        for org in organizations:
            org_slug = org['slug']
            print(f"\nMemberships for organization {org['name']} ({org_slug}):")
            memberships = get_organization_memberships(token, org_slug)
            if memberships:
                print(json.dumps(memberships, indent=2))
            
            print(f"\nSecurity Groups for organization {org['name']} ({org_slug}):")
            security_groups = get_security_groups(token, org_slug)
            if security_groups:
                print(json.dumps(security_groups, indent=2))

            print(f"\nLighthouses for organization {org['name']} ({org_slug}):")
            lighthouses = get_lighthouses(token, org_slug)
            if lighthouses:
                print(json.dumps(lighthouses, indent=2))

        # Step 5: Find an organization without security groups and create one
        print("\nLooking for an organization without security groups...")
        org_without_sg = find_org_without_security_groups(token)
        if org_without_sg:
            print(f"\nFound organization without security groups: {org_without_sg['name']}")
            print("Creating a new security group...")
            new_sg = create_security_group(token, org_without_sg['slug'])
            if new_sg:
                print("\nSuccessfully created security group:")
                print(json.dumps(new_sg, indent=2))
            else:
                print("\nFailed to create security group")
        else:
            print("\nNo organizations found without security groups")

        # Step 6: Find an organization without lighthouses and create one
        print("\nLooking for an organization without lighthouses...")
        org_without_lh = find_org_without_lighthouses(token)
        if org_without_lh:
            print(f"\nFound organization without lighthouses: {org_without_lh['name']}")
            print("Creating a new lighthouse...")
            new_lh = create_lighthouse(token, org_without_lh['slug'])
            if new_lh:
                print("\nSuccessfully created lighthouse:")
                print(json.dumps(new_lh, indent=2))
            else:
                print("\nFailed to create lighthouse")
        else:
            print("\nNo organizations found without lighthouses")
    else:
        print("\nNo organizations found or error retrieving organizations.")

if __name__ == "__main__":
    main() 