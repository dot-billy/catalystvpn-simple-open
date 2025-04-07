from rest_framework import serializers
from ..models import Membership
from .base import OrganizationScopedSerializer, UserSerializer


class MembershipSerializer(OrganizationScopedSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Membership
        fields = ('id', 'user', 'user_id', 'organization', 'role', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication required')

        # Ensure the user has permission to manage memberships
        organization_id = self.context.get('organization_id')
        if not organization_id:
            raise serializers.ValidationError('Organization context is required')

        # Get organization from ID
        from ..models import Organization
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError('Organization not found')

        user_membership = organization.memberships.filter(user=request.user).first()
        if not user_membership or user_membership.role != Membership.Roles.ADMIN:
            raise serializers.ValidationError('Only organization admins can manage memberships')

        return attrs 