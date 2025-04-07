import os
import subprocess
import tempfile
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import CertificateAuthority, Certificate
from ..serializers import CertificateAuthoritySerializer, CertificateSerializer
from .base import OrganizationOperatorViewSet


class CertificateAuthorityViewSet(OrganizationOperatorViewSet):
    queryset = CertificateAuthority.objects.all()
    serializer_class = CertificateAuthoritySerializer

    def get_queryset(self):
        """Filter queryset by organization."""
        organization_id = self.get_organization_id()
        print(f"Filtering CAs by organization: {organization_id}")
        return super().get_queryset().filter(organization_id=organization_id)

    def get_serializer_context(self):
        """Add organization and request to serializer context."""
        context = super().get_serializer_context()
        context['organization_id'] = self.get_organization_id()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        """Return the single CA for this organization if it exists."""
        organization_id = self.get_organization_id()
        try:
            ca = self.get_queryset().get(organization_id=organization_id)
            serializer = self.get_serializer(ca)
            return Response(serializer.data)
        except CertificateAuthority.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        """Generate CA certificate and save it."""
        organization_id = self.get_organization_id()
        
        # Create a temporary directory for certificate generation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate CA certificate using nebula-cert
            ca_crt_path = os.path.join(temp_dir, 'ca.crt')
            ca_key_path = os.path.join(temp_dir, 'ca.key')
            
            cmd = [
                'nebula-cert', 'ca',
                '-name', f'ca-{organization_id}',
                '-out-crt', ca_crt_path,
                '-out-key', ca_key_path
            ]
            
            try:
                subprocess.run(cmd, check=True)
                
                # Read the generated certificates
                with open(ca_crt_path, 'r') as f:
                    ca_cert = f.read()
                with open(ca_key_path, 'r') as f:
                    ca_key = f.read()
                
                # Save the CA with a 1-year validity
                expires_at = timezone.now() + timedelta(days=365)
                serializer.save(
                    organization_id=organization_id,
                    ca_cert=ca_cert,
                    ca_key=ca_key,
                    expires_at=expires_at
                )
                
            except subprocess.CalledProcessError as e:
                print(f"Error generating CA certificate: {e}")
                raise
            except Exception as e:
                print(f"Error saving CA: {e}")
                raise

    @action(detail=True, methods=['post'])
    def rotate(self, request, organization_id=None, pk=None):
        """Rotate the CA certificate."""
        ca = self.get_object()
        # TODO: Implement certificate rotation
        return Response({'status': 'Certificate rotation not implemented yet'})

    @action(detail=True, methods=['post'])
    def revoke(self, request, organization_id=None, pk=None):
        """Revoke the CA certificate."""
        ca = self.get_object()
        ca.revoked = True
        ca.revoked_at = timezone.now()
        ca.save()
        return Response({'status': 'Certificate revoked successfully'})


class CertificateViewSet(OrganizationOperatorViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    @action(detail=True, methods=['post'])
    def revoke(self, request, organization_id=None, pk=None):
        """Revoke a certificate."""
        cert = self.get_object()
        # TODO: Implement certificate revocation logic
        return Response({'status': 'Certificate revoked'})

    @action(detail=True, methods=['post'])
    def renew(self, request, organization_id=None, pk=None):
        """Renew a certificate."""
        cert = self.get_object()
        # TODO: Implement certificate renewal logic
        return Response({'status': 'Certificate renewal initiated'}) 