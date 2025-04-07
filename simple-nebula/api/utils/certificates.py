import os
import subprocess
import tempfile
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models import Certificate, CertificateAuthority


def generate_ca_certificate(organization, network, expires_at=None):
    """Generate a new CA certificate for an organization."""
    if expires_at is None:
        expires_at = timezone.now() + timedelta(days=365)

    # Create temporary directory for certificate generation
    with tempfile.TemporaryDirectory() as temp_dir:
        ca_key_path = os.path.join(temp_dir, 'ca.key')
        ca_cert_path = os.path.join(temp_dir, 'ca.crt')

        # Generate CA key and certificate
        try:
            # Generate CA private key
            subprocess.run(
                ['nebula-cert', 'ca', '-name', organization.name],
                cwd=temp_dir,
                check=True,
                capture_output=True
            )

            # Read generated files
            with open(ca_key_path, 'r') as f:
                ca_key = f.read()
            with open(ca_cert_path, 'r') as f:
                ca_cert = f.read()

            # Create CA in database
            return CertificateAuthority.objects.create(
                organization=organization,
                network=network,
                ca_cert=ca_cert,
                ca_key=ca_key,
                expires_at=expires_at
            )
        except subprocess.CalledProcessError as e:
            raise ValidationError(f'Failed to generate CA certificate: {e.stderr.decode()}')


def generate_node_certificate(node, ca, expires_at=None):
    """Generate a new certificate for a node."""
    if expires_at is None:
        expires_at = timezone.now() + timedelta(days=90)

    # Create temporary directory for certificate generation
    with tempfile.TemporaryDirectory() as temp_dir:
        ca_key_path = os.path.join(temp_dir, 'ca.key')
        ca_cert_path = os.path.join(temp_dir, 'ca.crt')
        node_key_path = os.path.join(temp_dir, 'node.key')
        node_cert_path = os.path.join(temp_dir, 'node.crt')

        try:
            # Write CA files
            with open(ca_key_path, 'w') as f:
                f.write(ca.ca_key)
            with open(ca_cert_path, 'w') as f:
                f.write(ca.ca_cert)

            # Get the network CIDR
            network_cidr = node.network.cidr if node.network else '192.168.100.0/24'
            # Extract the network mask from the CIDR
            network_mask = network_cidr.split('/')[1]
            # Create the full IP with CIDR
            ip_with_cidr = f"{node.nebula_ip}/{network_mask}"

            # Generate node certificate
            groups = list(node.security_groups.values_list('name', flat=True))
            groups_str = ','.join(groups) if groups else 'default'
            
            result = subprocess.run([
                'nebula-cert', 'sign',
                '-name', node.name,
                '-ip', ip_with_cidr,
                '-groups', groups_str,
                '-ca-crt', ca_cert_path,
                '-ca-key', ca_key_path,
                '-out-crt', node_cert_path,
                '-out-key', node_key_path
            ], cwd=temp_dir, check=True, capture_output=True, text=True)

            # Read generated files
            with open(node_key_path, 'r') as f:
                node_key = f.read()
            with open(node_cert_path, 'r') as f:
                node_cert = f.read()

            # Create certificate in database
            return Certificate.objects.create(
                ca=ca,
                cert_type=Certificate.CertificateTypes.NODE,
                cert=node_cert,
                key=node_key,
                expires_at=expires_at,
                nebula_ip=node.nebula_ip
            )
        except subprocess.CalledProcessError as e:
            raise ValidationError(f'Failed to generate node certificate: {e.stderr}')
        except Exception as e:
            raise ValidationError(f'Failed to generate node certificate: {str(e)}')


def generate_lighthouse_certificate(lighthouse, ca, expires_at=None):
    """Generate a new certificate for a lighthouse."""
    if expires_at is None:
        expires_at = timezone.now() + timedelta(days=90)

    # Create temporary directory for certificate generation
    with tempfile.TemporaryDirectory() as temp_dir:
        ca_key_path = os.path.join(temp_dir, 'ca.key')
        ca_cert_path = os.path.join(temp_dir, 'ca.crt')
        lighthouse_key_path = os.path.join(temp_dir, 'lighthouse.key')
        lighthouse_cert_path = os.path.join(temp_dir, 'lighthouse.crt')

        try:
            # Write CA files
            with open(ca_key_path, 'w') as f:
                f.write(ca.ca_key)
            with open(ca_cert_path, 'w') as f:
                f.write(ca.ca_cert)

            # Get the network CIDR
            network_cidr = lighthouse.network.cidr if lighthouse.network else '192.168.100.0/24'
            # Extract the network mask from the CIDR
            network_mask = network_cidr.split('/')[1]
            # Create the full IP with CIDR
            ip_with_cidr = f"{lighthouse.nebula_ip}/{network_mask}"

            # Generate lighthouse certificate with lighthouse group
            groups = list(lighthouse.security_groups.values_list('name', flat=True))
            groups.append('lighthouse')  # Add lighthouse group
            groups_str = ','.join(groups)
            
            result = subprocess.run([
                'nebula-cert', 'sign',
                '-name', lighthouse.name,
                '-ip', ip_with_cidr,
                '-groups', groups_str,
                '-ca-crt', ca_cert_path,
                '-ca-key', ca_key_path,
                '-out-crt', lighthouse_cert_path,
                '-out-key', lighthouse_key_path
            ], cwd=temp_dir, check=True, capture_output=True, text=True)

            # Read generated files
            with open(lighthouse_key_path, 'r') as f:
                lighthouse_key = f.read()
            with open(lighthouse_cert_path, 'r') as f:
                lighthouse_cert = f.read()

            # Create certificate in database
            return Certificate.objects.create(
                ca=ca,
                cert_type=Certificate.CertificateTypes.LIGHTHOUSE,
                cert=lighthouse_cert,
                key=lighthouse_key,
                expires_at=expires_at,
                nebula_ip=lighthouse.nebula_ip
            )
        except subprocess.CalledProcessError as e:
            raise ValidationError(f'Failed to generate lighthouse certificate: {e.stderr}')
        except Exception as e:
            raise ValidationError(f'Failed to generate lighthouse certificate: {str(e)}') 