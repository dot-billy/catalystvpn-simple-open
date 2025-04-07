from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Organization
from .base import BaseModelSerializer
from .membership import MembershipSerializer
from .certificates import CertificateAuthoritySerializer
from .network import LighthouseSerializer, NodeSerializer

User = get_user_model()


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class UserCreateSerializer(BaseModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class OrganizationSerializer(BaseModelSerializer):
    """
    Serializer for Organization model.
    
    This serializer handles the creation and management of organizations, including:
    - Basic organization information (name, slug, description)
    - Organization members and their roles
    - Certificate authority for device certificates
    - Associated lighthouses and nodes
    - Primary network configuration
    
    When creating an organization, you can specify:
    - Organization name (required)
    - Organization description (optional)
    - Network configuration (optional, defaults provided)
    """
    members = MembershipSerializer(
        source='memberships',
        many=True,
        read_only=True,
        help_text='List of organization members and their roles'
    )
    certificate_authority = CertificateAuthoritySerializer(
        read_only=True,
        help_text='Certificate authority for managing device certificates'
    )
    lighthouses = LighthouseSerializer(
        many=True,
        read_only=True,
        help_text='List of organization lighthouses'
    )
    nodes = NodeSerializer(
        many=True,
        read_only=True,
        help_text='List of organization nodes'
    )
    
    # Network configuration fields
    network_name = serializers.CharField(
        required=False,
        default='Primary Network',
        help_text='Name for the primary network that will be created with the organization'
    )
    network_cidr = serializers.CharField(
        required=False,
        default='192.168.100.0/24',
        help_text='CIDR range for the primary network (e.g., 192.168.100.0/24)'
    )
    network_description = serializers.CharField(
        required=False,
        default='Primary network for the organization',
        help_text='Description for the primary network'
    )

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'slug', 'description',
            'members', 'certificate_authority',
            'lighthouses', 'nodes',
            'network_name', 'network_cidr', 'network_description',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate organization data, including network CIDR."""
        data = super().validate(data)
        
        # Validate network CIDR if provided
        network_cidr = data.get('network_cidr', '192.168.100.0/24')
        from ..models.network import validate_cidr
        try:
            validate_cidr(network_cidr)
        except Exception as e:
            raise serializers.ValidationError({'network_cidr': str(e)})
            
        return data

    def create(self, validated_data):
        """
        Create a new organization with its primary network and certificate authority.
        
        This method:
        1. Creates the organization
        2. Creates an admin membership for the requesting user
        3. Creates a primary network with the specified configuration
        4. Creates a certificate authority for the organization
        """
        # Remove network-related fields from validated_data
        network_name = validated_data.pop('network_name', 'Primary Network')
        network_cidr = validated_data.pop('network_cidr', '192.168.100.0/24')
        network_description = validated_data.pop('network_description', 'Primary network for the organization')
        
        # Create the organization
        organization = super().create(validated_data)
        
        # Create admin membership
        from ..models import Membership
        Membership.objects.create(
            user=self.context['request'].user,
            organization=organization,
            role=Membership.Roles.ADMIN
        )
        
        # Create primary network
        from ..models import Network
        from django.core.exceptions import ValidationError
        try:
            network = Network(
                organization=organization,
                name=network_name,
                cidr=network_cidr,
                description=network_description,
                is_primary=True
            )
            network.full_clean()  # Run model validation
            network.save()
        except ValidationError as e:
            # If network creation fails, delete the organization and raise the error
            organization.delete()
            raise serializers.ValidationError({'network': e.message_dict})
        except Exception as e:
            # If network creation fails for any other reason, delete the organization and raise the error
            organization.delete()
            raise serializers.ValidationError({'network': str(e)})
        
        return organization 