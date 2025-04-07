import requests
import json

BASE_URL = "http://localhost:8000/api"

def get_token(email: str, password: str):
    """Get an authentication token."""
    url = f"{BASE_URL}/token/"
    response = requests.post(url, json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json()["access"]
    else:
        print(f"Failed to get token: {response.status_code} - {response.text}")
        return None

def add_firewall_rule(token, security_group_id, rule_data):
    """Add a firewall rule to a security group."""
    url = f"{BASE_URL}/organizations/deltaops/security-groups/{security_group_id}/add_rule/"
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

def main():
    # Admin credentials
    email = "myadminemail@gmail.com"
    password = "myAdminPassword"
    
    # Get token
    token = get_token(email, password)
    if not token:
        print("Failed to get token")
        return
    
    # Security group details
    security_group_id = "0eb1341d-29ae-4432-b93b-11e2a2e8a01a"
    
    # Add SSH firewall rule
    ssh_rule = {
        "rule_type": "inbound",  # Added required field
        "protocol": "tcp",
        "port": "22",  # Using string instead of integer
        "cidr": "0.0.0.0/0"
    }
    
    add_firewall_rule(token, security_group_id, ssh_rule)

if __name__ == "__main__":
    main() 