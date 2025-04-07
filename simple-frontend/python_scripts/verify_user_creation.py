import requests
import json
import sys
from typing import Dict, Optional, List
from datetime import datetime

BASE_URL = "http://myBackEndUrlOrIP:8000/api"

def get_token(email: str, password: str) -> Optional[str]:
    """Get JWT token by authenticating with email and password."""
    try:
        # Use the /token/ endpoint as discovered in the code
        print(f"Authenticating at {BASE_URL}/token/...")
        response = requests.post(
            f"{BASE_URL}/token/",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        data = response.json()
        print(f"Auth successful! Response keys: {list(data.keys())}")
        
        # Get the access token
        token = data.get("access")
        if not token:
            print(f"Warning: Could not find 'access' key in response. Available keys: {list(data.keys())}")
            # Try some other common keys
            token = data.get("token") or data.get("access_token")
            
        return token
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
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
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_organization_memberships(token: str, organization_slug: str) -> Optional[List[Dict]]:
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
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def create_user(token: str, organization_slug: str, organization_id: str, user_data: Dict) -> Optional[Dict]:
    """Create a user and add them to an organization."""
    try:
        # First, verify we have admin access to the organization
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        organization = response.json()
        
        # Check our own membership to confirm admin status
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/members/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        memberships = response.json()
        
        # Find our own membership
        our_admin_membership = None
        for membership in memberships:
            if membership.get('role') == 'admin':
                our_admin_membership = membership
                break
                
        if not our_admin_membership:
            print("  ✗ Not an admin of this organization. Cannot manage members.")
            return None
            
        print(f"  ✓ Confirmed admin access with membership ID: {our_admin_membership['id']}")
        
        # Then, check if user already exists
        response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            params={"email": user_data["email"]}
        )
        response.raise_for_status()
        users = response.json()
        
        user = None
        if users:
            # User exists, use existing user
            user = users[0]
            print(f"  ✓ User {user_data['email']} already exists, using existing account")
        else:
            # Create new user
            response = requests.post(
                f"{BASE_URL}/users/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "email": user_data["email"],
                    "password": user_data["password"],
                    "full_name": f"{user_data['first_name']} {user_data['last_name']}"
                }
            )
            response.raise_for_status()
            user = response.json()
            print(f"  ✓ Created new user account")
        
        # Check if user is already a member of the organization
        response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/members/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        all_memberships = response.json()
        
        # Find if the user is already a member
        existing_membership = None
        for membership in all_memberships:
            if membership.get('user', {}).get('id') == user["id"]:
                existing_membership = membership
                break
                
        if existing_membership:
            # User is already a member, update their role
            response = requests.patch(
                f"{BASE_URL}/organizations/{organization_slug}/members/{existing_membership['id']}/",
                headers={"Authorization": f"Bearer {token}"},
                json={"role": user_data["role"]}
            )
            response.raise_for_status()
            print(f"  ✓ Updated existing membership role to {user_data['role']}")
            return response.json()
        else:
            # Create new membership
            response = requests.post(
                f"{BASE_URL}/organizations/{organization_slug}/members/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "user_id": user["id"],
                    "role": user_data["role"]
                }
            )
            response.raise_for_status()
            print(f"  ✓ Created new membership with {user_data['role']} role")
            return response.json()
            
    except requests.exceptions.RequestException as e:
        print(f"Error creating user: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_current_user(token: str) -> Optional[Dict]:
    """Get the current user's profile."""
    try:
        response = requests.get(
            f"{BASE_URL}/users/me/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting current user: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
            
        # If the /me/ endpoint fails, try getting it by making a regular request
        # to the /users/ endpoint (this is inefficient but might work as a backup)
        try:
            print("Trying backup method to get current user...")
            response = requests.get(
                f"{BASE_URL}/users/",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            users = response.json()
            if users and isinstance(users, list) and len(users) > 0:
                return users[0]  # just return the first user
        except requests.exceptions.RequestException as e2:
            print(f"Backup method also failed: {e2}")
            
        return None

def is_admin_of_organization(token: str, organization_slug: str) -> bool:
    """Check if the current user is an admin of the organization."""
    try:
        # First, get the organization details
        org_response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        org_response.raise_for_status()
        organization = org_response.json()
        
        # Then get all memberships
        memberships_response = requests.get(
            f"{BASE_URL}/organizations/{organization_slug}/members/",
            headers={"Authorization": f"Bearer {token}"}
        )
        memberships_response.raise_for_status()
        memberships = memberships_response.json()
        
        # Get current user
        user_response = requests.get(
            f"{BASE_URL}/users/me/",
            headers={"Authorization": f"Bearer {token}"}
        )
        user_response.raise_for_status()
        current_user = user_response.json()
        
        # Find the current user's membership
        for membership in memberships:
            if membership.get('user', {}).get('id') == current_user.get('id'):
                print(f"Found my membership: {membership}")
                return membership.get('role') == 'admin'
                
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error checking admin status: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python verify_user_creation.py <admin_email> <admin_password>")
        sys.exit(1)

    admin_email = sys.argv[1]
    admin_password = sys.argv[2]

    print(f"\nTesting authentication for admin user {admin_email}...")
    
    # Step 1: Get JWT token for admin
    token = get_token(admin_email, admin_password)
    if not token:
        print("Failed to get token. Exiting.")
        sys.exit(1)
    print("Successfully obtained admin token!")
    
    # Get current user
    current_user = get_current_user(token)
    if not current_user:
        print("Failed to get current user. Exiting.")
        sys.exit(1)
    print(f"Authenticated as: {current_user.get('email')} (ID: {current_user.get('id')})")

    # Step 2: Get organizations
    organizations = get_organizations(token)
    if not organizations:
        print("No organizations found or error retrieving organizations.")
        sys.exit(1)

    print("\nChecking organizations:")
    for org in organizations:
        org_slug = org['slug']
        org_id = org['id']  # Get the organization's UUID
        print(f"\nOrganization: {org['name']} ({org_slug})")
        
        # Check admin membership - using direct check
        is_admin = is_admin_of_organization(token, org_slug)
        
        if not is_admin:
            print("✗ Not an admin of this organization. Skipping...")
            continue
        
        print("✓ Confirmed admin access")
        
        # Create test users with different roles
        test_users = [
            {
                "email": f"test_admin_{org_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "Admin",
                "role": "admin"
            },
            {
                "email": f"test_operator_{org_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "Operator",
                "role": "operator"
            },
            {
                "email": f"test_user_{org_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "User",
                "role": "viewer"
            }
        ]
        
        print("\nCreating test users:")
        for user_data in test_users:
            print(f"\nCreating {user_data['role']} user {user_data['email']}...")
            membership = create_user(token, org_slug, org_id, user_data)
            if membership:
                print(f"✓ Successfully created {user_data['role']} user")
                print(f"  ID: {membership['id']}")
                print(f"  Name: {membership['user']['full_name']}")
                print(f"  Role: {membership['role']}")
            else:
                print(f"✗ Failed to create {user_data['role']} user")

if __name__ == "__main__":
    main() 