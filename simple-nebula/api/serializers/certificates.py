from rest_framework import serializers
from ..models import CertificateAuthority, Certificate
from .base import OrganizationScopedSerializer


class CertificateAuthoritySerializer(OrganizationScopedSerializer):
    class Meta:
        model = CertificateAuthority
        fields = (
            'id', 'organization', 'network', 'ca_cert', 'expires_at',
            'revoked', 'revoked_at', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'ca_cert', 'ca_key', 'created_at',
            'updated_at', 'revoked', 'revoked_at'
        )


class CertificateSerializer(OrganizationScopedSerializer):
    class Meta:
        model = Certificate
        fields = (
            'id', 'ca', 'cert_type', 'cert', 'expires_at',
            'revoked', 'revoked_at', 'nebula_ip',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'cert', 'key', 'created_at',
            'updated_at', 'revoked', 'revoked_at'
        )

    def validate(self, attrs):
        # Ensure the CA belongs to the same organization
        ca = attrs.get('ca')
        organization_id = self.context.get('organization_id')
        if ca and ca.organization_id != organization_id:
            raise serializers.ValidationError(
                'Certificate Authority must belong to the same organization'
            )
        return attrs 