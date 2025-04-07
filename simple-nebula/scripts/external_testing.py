#!/usr/bin/env python3
import os
import sys
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
API_URL = "http://web:8000/api"
ADMIN_EMAIL = "myadminemail@gmail.com"
ADMIN_PASSWORD = "myAdminPassword"

def get_auth_token() -> str:
    """Get JWT token for authentication."""
    response = requests.post(
        f"{API_URL}/token/",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    response.raise_for_status()
    return response.json()["access"]

def create_organization(token: str) -> Dict[str, Any]:
    """Create a test organization."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    response = requests.post(
        f"{API_URL}/organizations/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": f"Test Organization {timestamp}",
            "slug": f"test-organization-{timestamp}",
            "description": "Test organization for external testing"
        }
    )
    response.raise_for_status()
    return response.json()

def create_network(token: str, organization_id: str) -> Dict[str, Any]:
    """Create a test network."""
    response = requests.post(
        f"{API_URL}/organizations/{organization_id}/networks/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Network",
            "cidr": "192.168.100.0/24",
            "description": "Test network for external testing",
            "is_primary": True
        }
    )
    response.raise_for_status()
    return response.json()

def create_lighthouse(token: str, organization_id: str, network_id: str) -> Dict[str, Any]:
    """Create a test lighthouse."""
    response = requests.post(
        f"{API_URL}/organizations/{organization_id}/lighthouses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Lighthouse",
            "hostname": "test-lighthouse.example.com",
            "network": network_id,
            "public_ip": "192.168.1.100",
            "port": 4242
        }
    )
    response.raise_for_status()
    return response.json()

def create_second_lighthouse(token: str, organization_id: str, network_id: str) -> Dict[str, Any]:
    """Create a second test lighthouse."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    response = requests.post(
        f"{API_URL}/organizations/{organization_id}/lighthouses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": f"Test Lighthouse {timestamp}",
            "hostname": "test-lighthouse-2.example.com",
            "network": network_id,
            "public_ip": "192.168.1.101",
            "port": 4242
        }
    )
    response.raise_for_status()
    return response.json()

def test_lighthouse_creation():
    """Test lighthouse creation and configuration."""
    try:
        # Get authentication token
        print("Getting authentication token...")
        token = get_auth_token()

        # Create organization
        print("\nCreating test organization...")
        org = create_organization(token)
        print(f"Created organization: {org['name']}")

        # Get primary network
        print("\nGetting primary network...")
        response = requests.get(
            f"{API_URL}/organizations/{org['id']}/networks/",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        networks = response.json()
        primary_network = next(network for network in networks if network['is_primary'])
        print(f"Using primary network: {primary_network['name']}")

        # Create first lighthouse
        print("\nCreating first test lighthouse...")
        lighthouse = create_lighthouse(token, org['id'], primary_network['id'])
        print(f"Created lighthouse: {lighthouse['name']}")
        print(f"Nebula IP: {lighthouse['nebula_ip']}")
        print(f"Public IP: {lighthouse['public_ip']}")
        print(f"Port: {lighthouse['port']}")
        print(f"API Key: {lighthouse.get('api_key')}")
        print(f"Configuration: {json.dumps(lighthouse['config'], indent=2)}")

        # Create second lighthouse
        print("\nCreating second test lighthouse...")
        lighthouse2 = create_second_lighthouse(token, org['id'], primary_network['id'])
        print(f"Created second lighthouse: {lighthouse2['name']}")
        print(f"Nebula IP: {lighthouse2['nebula_ip']}")
        print(f"Public IP: {lighthouse2['public_ip']}")
        print(f"Port: {lighthouse2['port']}")
        print(f"API Key: {lighthouse2.get('api_key')}")
        print(f"Configuration: {json.dumps(lighthouse2['config'], indent=2)}")

        # Verify that the lighthouses have different Nebula IPs
        if lighthouse['nebula_ip'] == lighthouse2['nebula_ip']:
            raise Exception(f"Both lighthouses have the same Nebula IP: {lighthouse['nebula_ip']}")

        print("\n✅ Lighthouse tests completed successfully!")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error during lighthouse tests: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    test_lighthouse_creation() 