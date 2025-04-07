from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Network, SecurityGroup, Lighthouse
from django.db import connection
from ..utils.certificates import generate_lighthouse_certificate, generate_node_certificate

User = get_user_model()


class BaseModelSerializer(serializers.ModelSerializer):
    """Base serializer for all models."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"BaseModelSerializer init context: {self.context}")
        # Ensure the context is passed to child serializers
        for field_name, field in self.fields.items():
            if hasattr(field, 'context') and not isinstance(field, serializers.SerializerMethodField):
                try:
                    field.context = self.context
                except AttributeError:
                    # Skip if the field doesn't allow setting context (e.g., read-only serializers)
                    pass

    def get_fields(self):
        fields = super().get_fields()
        # Ensure context is passed to all fields
        for field in fields.values():
            if hasattr(field, 'context') and not isinstance(field, serializers.SerializerMethodField):
                try:
                    field.context = self.context
                except AttributeError:
                    pass
        return fields

    def create(self, validated_data):
        print(f"BaseModelSerializer create validated_data: {validated_data}")
        print(f"BaseModelSerializer create context: {self.context}")
        # Ensure the context is passed to the model's create method
        if hasattr(self.Meta.model, 'create'):
            return self.Meta.model.create(**validated_data)
        # If the model doesn't have a create method, use the default create
        return self.Meta.model.objects.create(**validated_data)


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


class OrganizationScopedSerializer(BaseModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        organization_id = self.context.get('organization_id')
        print(f"OrganizationScopedSerializer init context: {self.context}")
        print(f"OrganizationScopedSerializer init organization_id: {organization_id}")

    def validate(self, data):
        data = super().validate(data)
        organization_id = self.context.get('organization_id')
        print(f"OrganizationScopedSerializer validate context: {self.context}")
        print(f"OrganizationScopedSerializer validate data: {data}")
        if not organization_id:
            raise serializers.ValidationError('Organization ID is required')
        return data

    def create(self, validated_data):
        organization_id = self.context.get('organization_id')
        print(f"OrganizationScopedSerializer create organization_id: {organization_id}")
        print(f"OrganizationScopedSerializer create organization_id type: {type(organization_id)}")
        if not organization_id:
            raise serializers.ValidationError('Organization ID is required')

        # Ensure organization_id is a string
        organization_id = str(organization_id)
        validated_data['organization_id'] = organization_id
        
        # Create the instance with the organization_id
        instance = super().create(validated_data)
        
        # Ensure the organization is set on the instance
        if not instance.organization_id:
            instance.organization_id = organization_id
            instance.save()
            
        return instance


class BaseNodeSerializer(OrganizationScopedSerializer):
    certificate = serializers.PrimaryKeyRelatedField(read_only=True)
    security_groups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    security_group_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        organization_id = self.context.get('organization_id')
        if organization_id:
            self.fields['network'] = serializers.PrimaryKeyRelatedField(
                queryset=Network.objects.filter(organization_id=organization_id),
                required=False,
                allow_null=True
            )
        else:
            self.fields['network'] = serializers.PrimaryKeyRelatedField(
                queryset=Network.objects.none(),
                required=False,
                allow_null=True
            )

    class Meta:
        abstract = True
        fields = (
            'id', 'organization', 'name', 'hostname', 'nebula_ip',
            'certificate', 'security_groups', 'security_group_ids',
            'network', 'created_at', 'updated_at', 'config'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'config')
        extra_kwargs = {
            'name': {'required': True},
            'hostname': {'required': True},
            'nebula_ip': {'required': False},  # We'll auto-assign if not provided
        }

    def validate_network(self, value):
        if value is None:
            # Get organization from context
            organization_id = str(self.context.get('organization_id'))
            if not organization_id:
                raise serializers.ValidationError('Organization context is required')
            
            # Get primary network
            primary_network = Network.objects.filter(
                organization_id=organization_id,
                is_primary=True
            ).first()
            
            if not primary_network:
                raise serializers.ValidationError('No primary network found for this organization')
            
            return primary_network
            
        organization_id = str(self.context.get('organization_id'))
        if not organization_id:
            raise serializers.ValidationError('Organization context is required')

        # Get the network's organization ID from the database
        network = Network.objects.get(id=value.id)
        network_org_id = str(network.organization_id)

        # Ensure the network exists and belongs to the organization
        if network_org_id != organization_id:
            print(f"Network organization ID: {network_org_id} ({type(network_org_id)})")
            print(f"Expected organization ID: {organization_id} ({type(organization_id)})")
            print(f"Network organization ID from value: {str(value.organization_id)} ({type(value.organization_id)})")
            print(f"Network organization ID from DB: {network_org_id} ({type(network_org_id)})")
            print(f"Network organization ID from DB raw: {network.organization_id}")
            print(f"Network organization ID from value raw: {value.organization_id}")
            raise serializers.ValidationError('Network must belong to the same organization')
        
        return value

    def validate_security_group_ids(self, value):
        organization_id = self.context.get('organization_id')
        if not organization_id:
            raise serializers.ValidationError('Organization context is required')

        security_groups = SecurityGroup.objects.filter(
            id__in=value,
            organization_id=organization_id
        )
        if len(security_groups) != len(value):
            raise serializers.ValidationError(
                'Some security groups do not exist or do not belong to this organization'
            )
        return value

    def validate_nebula_ip(self, value):
        if value is None:
            return value
        network = self.initial_data.get('network')
        if network:
            network_obj = Network.objects.get(id=network)
            if not network_obj.is_ip_available(value):
                raise serializers.ValidationError(
                    'IP address is not available in this network'
                )
        return value

    def create(self, validated_data):
        print(f"BaseNodeSerializer create validated_data: {validated_data}")
        security_group_ids = validated_data.pop('security_group_ids', [])
        # If nebula_ip not provided, get next available IP
        if 'nebula_ip' not in validated_data:
            network = validated_data.get('network')
            if network:
                validated_data['nebula_ip'] = network.get_available_ip()
        # Ensure organization_id is set
        organization_id = self.context.get('organization_id')
        if not organization_id:
            raise serializers.ValidationError('Organization context is required')
        validated_data['organization_id'] = organization_id
        
        # Create the instance
        instance = super().create(validated_data)
        
        # Set security groups if provided
        if security_group_ids:
            instance.security_groups.set(security_group_ids)
            
        # Don't generate certificate here - let the child serializer handle it
        return instance

    def update(self, instance, validated_data):
        security_group_ids = validated_data.pop('security_group_ids', None)
        instance = super().update(instance, validated_data)
        if security_group_ids is not None:
            instance.security_groups.set(security_group_ids)
        return instance 