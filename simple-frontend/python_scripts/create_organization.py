#!/usr/bin/env python3
"""
Script to create organizations and their components using CLI arguments or CSV input.
"""

import argparse
import csv
import json
import requests
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
import yaml

# Configuration
API_URL = "http://myBackEndUrlOrIP:8000/api"
ADMIN_EMAIL = "myadminemail@gmail.com"
ADMIN_PASSWORD = "myAdminPassword"

class OrganizationCreator:
    """Client for creating organizations and their components."""
    
    def __init__(self, base_url: str = "http://myBackEndUrlOrIP:8000"):
        """Initialize the client.
        
        Args:
            base_url: The base URL of the API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token: Optional[str] = None

    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the API.
        
        Args:
            email: Admin email
            password: Admin password
            
        Returns:
            bool: True if authentication successful
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/token/",
                json={'email': email, 'password': password}
            )
            response.raise_for_status()
            self.access_token = response.json()['access']
            return True
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

    def create_security_group(self, organization_id: str, name: str, description: str = "", 
                            firewall_rules: List[Dict] = None) -> Optional[Dict]:
        """Create a security group.
        
        Args:
            organization_id: Organization ID
            name: Security group name
            description: Security group description
            firewall_rules: List of firewall rules
            
        Returns:
            Optional[Dict]: Security group data if successful
        """
        try:
            # First create the security group
            data = {
                "name": name,
                "description": description
            }
            
            response = self.session.post(
                f"{self.base_url}/api/organizations/{organization_id}/security-groups/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json=data
            )
            response.raise_for_status()
            security_group = response.json()
            
            # Then add the firewall rules if any
            if firewall_rules:
                for rule in firewall_rules:
                    rule_data = {
                        "rule_type": rule.get("rule_type", "inbound"),
                        "protocol": rule.get("protocol", "tcp"),
                        "port": rule.get("port"),
                        "cidr": rule.get("cidr")
                    }
                    
                    # Remove None values
                    rule_data = {k: v for k, v in rule_data.items() if v is not None}
                    
                    response = self.session.post(
                        f"{self.base_url}/api/organizations/{organization_id}/security-groups/{security_group['id']}/add_rule/",
                        headers={"Authorization": f"Bearer {self.access_token}"},
                        json=rule_data
                    )
                    response.raise_for_status()
            
            return security_group
        except Exception as e:
            print(f"Failed to create security group: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {e.response.text}")
            return None

    def add_firewall_rule(self, organization_id: str, security_group_id: str, 
                         rule_type: str, protocol: str, port: Optional[int] = None,
                         cidr: Optional[str] = None, group: Optional[str] = None) -> Optional[Dict]:
        """Add a firewall rule to a security group.
        
        Args:
            organization_id: Organization ID
            security_group_id: Security group ID
            rule_type: Rule type (inbound/outbound)
            protocol: Protocol (tcp/udp/icmp/any)
            port: Port number (required for tcp/udp)
            cidr: CIDR notation (required if group not specified)
            group: Security group ID to reference (required if cidr not specified)
            
        Returns:
            Optional[Dict]: Firewall rule data if successful
        """
        try:
            data = {
                "rule_type": rule_type,
                "protocol": protocol
            }
            
            if port is not None:
                data["port"] = port
            if cidr:
                data["cidr"] = cidr
            if group:
                data["group"] = group
                
            response = self.session.post(
                f"{self.base_url}/api/organizations/{organization_id}/security-groups/{security_group_id}/add_rule/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to add firewall rule: {str(e)}")
            return None

    def create_organization(self, name: str, network_cidr: str = "192.168.100.0/24") -> Optional[Dict]:
        """Create a new organization with its primary network.
        
        Args:
            name: Organization name
            network_cidr: CIDR for the primary network
            
        Returns:
            Optional[Dict]: Organization data if successful
        """
        try:
            # Convert name to slug (lowercase, replace spaces with hyphens)
            slug = name.lower().replace(' ', '-')
            
            # Create the organization with network configuration
            response = self.session.post(
                f"{self.base_url}/api/organizations/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={
                    "name": name,
                    "slug": slug,
                    "network_name": f"{name} Primary Network",
                    "network_cidr": network_cidr,
                    "network_description": f"Primary network for {name}"
                }
            )
            
            if response.status_code == 400:
                error_data = response.json()
                print(f"Failed to create organization: {error_data}")
                return None
                
            response.raise_for_status()
            org_data = response.json()
            
            return org_data
        except Exception as e:
            print(f"Failed to create organization: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {e.response.text}")
            return None

    def create_lighthouse(self, organization_id: str, network_id: str, 
                         name: str, hostname: str, public_ip: str, port: int = 4242,
                         security_group_ids: List[str] = None) -> Optional[Dict]:
        """Create a lighthouse in the organization.
        
        Args:
            organization_id: Organization ID
            network_id: Network ID
            name: Lighthouse name
            hostname: Lighthouse hostname
            public_ip: Lighthouse public IP
            port: Lighthouse port
            security_group_ids: List of security group IDs
            
        Returns:
            Optional[Dict]: Lighthouse data if successful
        """
        try:
            data = {
                "name": name,
                "hostname": hostname,
                "public_ip": public_ip,
                "port": port,
                "network": network_id,
                "is_active": True
            }
            
            if security_group_ids:
                data["security_group_ids"] = security_group_ids
                
            response = self.session.post(
                f"{self.base_url}/api/organizations/{organization_id}/lighthouses/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to create lighthouse: {str(e)}")
            return None

    def create_node(self, organization_id: str, network_id: str, lighthouse_id: str,
                   name: str, hostname: str, security_group_ids: List[str] = None) -> Optional[Dict]:
        """Create a node in the organization.
        
        Args:
            organization_id: Organization ID
            network_id: Network ID
            lighthouse_id: Lighthouse ID to connect to
            name: Node name
            hostname: Node hostname
            security_group_ids: List of security group IDs
            
        Returns:
            Optional[Dict]: Node data if successful
        """
        try:
            data = {
                "name": name,
                "hostname": hostname,
                "network": network_id,
                "lighthouse": lighthouse_id
            }
            
            if security_group_ids:
                data["security_group_ids"] = security_group_ids
                
            response = self.session.post(
                f"{self.base_url}/api/organizations/{organization_id}/nodes/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to create node: {str(e)}")
            return None

    def get_primary_network(self, organization_id: str) -> Optional[Dict]:
        """Get the primary network for an organization.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            Optional[Dict]: Network data if successful
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/organizations/{organization_id}/networks/",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            networks = response.json()
            return next((net for net in networks if net['is_primary']), None)
        except Exception as e:
            print(f"Failed to get primary network: {str(e)}")
            return None

    def generate_configs(self, organization_id: str, network_id: str):
        """Generate configuration files for all devices.
        
        Args:
            organization_id: Organization ID
            network_id: Network ID
        """
        # Create base directory for configurations
        base_dir = os.path.join('configs', organization_id, network_id)
        os.makedirs(base_dir, exist_ok=True)

        # Custom YAML dumper that preserves certificate formatting
        class CertDumper(yaml.Dumper):
            def increase_indent(self, flow=False, *args, **kwargs):
                return super().increase_indent(flow, False)

            def represent_str(self, data):
                if '-----BEGIN' in data and '-----END' in data:
                    data = data.strip()
                    data = data.replace('\r\n', '\n')
                    data = data.replace('\n\n', '\n')
                    data = data.replace(' \n', '\n')
                    data = data.replace('\\n', '\n')
                    data = data.rstrip('\n')
                    return self.represent_scalar('tag:yaml.org,2002:str', data, style='|')
                return super().represent_str(data)

        CertDumper.add_representer(str, CertDumper.represent_str)

        # Get and save lighthouse configurations
        lighthouses = self._get_lighthouses(organization_id)
        for lighthouse in lighthouses:
            lighthouse_dir = os.path.join(base_dir, 'lighthouses', lighthouse['id'])
            os.makedirs(lighthouse_dir, exist_ok=True)

            config = self._get_lighthouse_config(organization_id, lighthouse['id'])
            if 'pki' in config:
                for key in ['ca', 'cert', 'key']:
                    if key in config['pki']:
                        cert = config['pki'][key]
                        cert = cert.strip()
                        cert = cert.replace('\r\n', '\n')
                        cert = cert.replace('\n\n', '\n')
                        cert = cert.replace(' \n', '\n')
                        cert = cert.replace('\\n', '\n')
                        cert = cert.rstrip('\n')
                        config['pki'][key] = cert

            with open(os.path.join(lighthouse_dir, 'config.yml'), 'w') as f:
                yaml.dump(config, f, Dumper=CertDumper, sort_keys=False, default_flow_style=False)

            if lighthouse.get('api_key'):
                with open(os.path.join(lighthouse_dir, 'api_key.txt'), 'w') as f:
                    f.write(lighthouse['api_key'])

        # Get and save node configurations
        nodes = self._get_nodes(organization_id)
        for node in nodes:
            node_dir = os.path.join(base_dir, 'nodes', node['id'])
            os.makedirs(node_dir, exist_ok=True)

            config = self._get_node_config(organization_id, node['id'])
            if 'pki' in config:
                for key in ['ca', 'cert', 'key']:
                    if key in config['pki']:
                        cert = config['pki'][key]
                        cert = cert.strip()
                        cert = cert.replace('\r\n', '\n')
                        cert = cert.replace('\n\n', '\n')
                        cert = cert.replace(' \n', '\n')
                        cert = cert.replace('\\n', '\n')
                        cert = cert.rstrip('\n')
                        config['pki'][key] = cert

            with open(os.path.join(node_dir, 'config.yml'), 'w') as f:
                yaml.dump(config, f, Dumper=CertDumper, sort_keys=False, default_flow_style=False)

            if node.get('api_key'):
                with open(os.path.join(node_dir, 'api_key.txt'), 'w') as f:
                    f.write(node['api_key'])

    def _get_lighthouses(self, organization_id: str) -> List[Dict]:
        """Get all lighthouses for an organization."""
        response = self.session.get(
            f"{self.base_url}/api/organizations/{organization_id}/lighthouses/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        response.raise_for_status()
        return response.json()

    def _get_nodes(self, organization_id: str) -> List[Dict]:
        """Get all nodes for an organization."""
        response = self.session.get(
            f"{self.base_url}/api/organizations/{organization_id}/nodes/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        response.raise_for_status()
        return response.json()

    def _get_lighthouse_config(self, organization_id: str, lighthouse_id: str) -> Dict:
        """Get lighthouse configuration."""
        response = self.session.get(
            f"{self.base_url}/api/organizations/{organization_id}/lighthouses/{lighthouse_id}/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        response.raise_for_status()
        lighthouse_data = response.json()
        
        ca_response = self.session.get(
            f"{self.base_url}/api/organizations/{organization_id}/ca/{lighthouse_data['certificate']['ca']}/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        ca_response.raise_for_status()
        ca_data = ca_response.json()
        
        return {
            'pki': {
                'ca': ca_data.get('ca_cert', ''),
                'cert': lighthouse_data['certificate']['cert'],
                'key': lighthouse_data['certificate'].get('key', ''),
            },
            'tun': {
                'mtu': 1300,
                'disabled': False,
                'tx_queue': 500,
                'drop_multicast': False,
                'drop_local_broadcast': False,
            },
            'relay': {
                'am_relay': False,
                'use_relays': True,
            },
            'cipher': 'aes',
            'listen': {
                'host': '0.0.0.0',
                'port': lighthouse_data['port'],
            },
            'punchy': {
                'punch': True,
            },
            'logging': {
                'level': 'info',
                'format': 'text',
            },
            'firewall': {
                'inbound': None,
                'outbound': None,
                'conntrack': {
                    'tcp_timeout': '12m',
                    'udp_timeout': '3m',
                    'default_timeout': '10m',
                },
                'inbound_action': 'drop',
                'outbound_action': 'drop',
            },
            'lighthouse': {
                'hosts': [],
                'interval': 60,
                'am_lighthouse': True,
            },
            'static_host_map': None,
        }

    def _get_node_config(self, organization_id: str, node_id: str) -> Dict:
        """Get node configuration."""
        response = self.session.get(
            f"{self.base_url}/api/organizations/{organization_id}/nodes/{node_id}/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        response.raise_for_status()
        return response.json().get('config', {})

def create_from_csv(csv_file: str, creator: OrganizationCreator):
    """Create organizations and components from a CSV file.
    
    Args:
        csv_file: Path to CSV file
        creator: OrganizationCreator instance
    """
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"\nProcessing organization: {row['organization_name']}")
            
            # Create organization
            org = creator.create_organization(
                name=row['organization_name'],
                network_cidr=row.get('network_cidr', '192.168.100.0/24')
            )
            if not org:
                print(f"Failed to create organization {row['organization_name']}")
                continue
                
            print(f"Created organization: {org['name']}")
            
            # Get primary network
            network = creator.get_primary_network(org['id'])
            if not network:
                print(f"No primary network found for {org['name']}")
                continue
                
            print(f"Using primary network: {network['name']}")
            
            # Create security groups if specified
            security_groups = {}
            if 'security_groups' in row:
                for sg_name, sg_rules in json.loads(row['security_groups']).items():
                    sg = creator.create_security_group(
                        organization_id=org['id'],
                        name=sg_name,
                        description=f"Security group for {sg_name}",
                        firewall_rules=sg_rules
                    )
                    if sg:
                        security_groups[sg_name] = sg['id']
                        print(f"Created security group: {sg_name}")
            
            # Create lighthouse
            lighthouse = creator.create_lighthouse(
                organization_id=org['id'],
                network_id=network['id'],
                name=row['lighthouse_name'],
                hostname=row['lighthouse_hostname'],
                public_ip=row['lighthouse_public_ip'],
                security_group_ids=[security_groups.get('lighthouse')] if 'lighthouse' in security_groups else None
            )
            if not lighthouse:
                print(f"Failed to create lighthouse for {org['name']}")
                continue
                
            print(f"Created lighthouse: {lighthouse['name']}")
            
            # Create nodes
            node_names = row['node_names'].split(',')
            node_hostnames = row['node_hostnames'].split(',')
            
            for name, hostname in zip(node_names, node_hostnames):
                node = creator.create_node(
                    organization_id=org['id'],
                    network_id=network['id'],
                    lighthouse_id=lighthouse['id'],
                    name=name.strip(),
                    hostname=hostname.strip(),
                    security_group_ids=[security_groups.get('node')] if 'node' in security_groups else None
                )
                if node:
                    print(f"Created node: {node['name']}")
                else:
                    print(f"Failed to create node {name}")
            
            # Generate configurations
            creator.generate_configs(org['id'], network['id'])
            print(f"Generated configurations for {org['name']}")

def main():
    parser = argparse.ArgumentParser(description='Create organizations and their components')
    parser.add_argument('--name', required=True, help='Organization name')
    parser.add_argument('--lighthouse-name', required=True, help='Lighthouse name')
    parser.add_argument('--lighthouse-hostname', required=True, help='Lighthouse hostname')
    parser.add_argument('--lighthouse-ip', required=True, help='Lighthouse public IP')
    parser.add_argument('--node-names', required=True, help='Comma-separated list of node names')
    parser.add_argument('--node-hostnames', required=True, help='Comma-separated list of node hostnames')
    parser.add_argument('--security-groups', help='JSON string containing security group configurations')
    parser.add_argument('--csv', help='CSV file containing organization details')
    parser.add_argument('--base-url', default='http://myBackEndUrlOrIP:8000', help='API base URL')
    parser.add_argument('--admin-email', default=ADMIN_EMAIL, help='Admin email')
    parser.add_argument('--admin-password', default=ADMIN_PASSWORD, help='Admin password')
    
    args = parser.parse_args()
    
    creator = OrganizationCreator(base_url=args.base_url)
    if not creator.authenticate(args.admin_email, args.admin_password):
        print("Authentication failed")
        sys.exit(1)
    
    if args.csv:
        create_from_csv(args.csv, creator)
        return
        
    # Create organization
    org = creator.create_organization(args.name)
    if not org:
        print("Failed to create organization")
        sys.exit(1)
    print(f"Created organization: {org['name']}")
    
    # Get primary network
    network = creator.get_primary_network(org['id'])
    if not network:
        print("Failed to get primary network")
        sys.exit(1)
    print(f"Using network: {network['name']}")
    
    # Parse security groups if provided
    security_groups = {}
    if args.security_groups:
        try:
            security_groups = json.loads(args.security_groups)
        except json.JSONDecodeError as e:
            print(f"Failed to parse security groups JSON: {e}")
            sys.exit(1)
    
    # Create lighthouse security group if specified
    lighthouse_security_group = None
    if 'lighthouse' in security_groups:
        lighthouse_security_group = creator.create_security_group(
            org['id'],
            f"{args.name}-lighthouse-sg",
            "Security group for lighthouse",
            security_groups['lighthouse']
        )
        if not lighthouse_security_group:
            print("Failed to create lighthouse security group")
            sys.exit(1)
        print(f"Created lighthouse security group: {lighthouse_security_group['name']}")
    
    # Create lighthouse
    lighthouse = creator.create_lighthouse(
        org['id'],
        network['id'],
        args.lighthouse_name,
        args.lighthouse_hostname,
        args.lighthouse_ip,
        security_group_ids=[lighthouse_security_group['id']] if lighthouse_security_group else None
    )
    if not lighthouse:
        print("Failed to create lighthouse")
        sys.exit(1)
    print(f"Created lighthouse: {lighthouse['name']}")
    
    # Create node security group if specified
    node_security_group = None
    if 'node' in security_groups:
        node_security_group = creator.create_security_group(
            org['id'],
            f"{args.name}-node-sg",
            "Security group for nodes",
            security_groups['node']
        )
        if not node_security_group:
            print("Failed to create node security group")
            sys.exit(1)
        print(f"Created node security group: {node_security_group['name']}")
    
    # Create nodes
    node_names = args.node_names.split(',')
    node_hostnames = args.node_hostnames.split(',')
    
    if len(node_names) != len(node_hostnames):
        print("Number of node names must match number of node hostnames")
        sys.exit(1)
    
    for name, hostname in zip(node_names, node_hostnames):
        node = creator.create_node(
            org['id'],
            network['id'],
            lighthouse['id'],
            name.strip(),
            hostname.strip(),
            security_group_ids=[node_security_group['id']] if node_security_group else None
        )
        if not node:
            print(f"Failed to create node: {name}")
            sys.exit(1)
        print(f"Created node: {node['name']}")
    
    # Generate configs
    creator.generate_configs(org['id'], network['id'])
    print("Generated configuration files")

if __name__ == "__main__":
    main() 