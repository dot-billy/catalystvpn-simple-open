from rest_framework import serializers
from ..models import SecurityGroup, Node, Lighthouse, Certificate, Network, APIKey, FirewallRule
from .base import OrganizationScopedSerializer
from .certificates import CertificateSerializer
from ..utils.certificates import generate_node_certificate, generate_lighthouse_certificate
from ..utils.config import generate_node_config, generate_lighthouse_config
import secrets
from ipaddress import IPv4Network


class NetworkSerializer(OrganizationScopedSerializer):
    name = serializers.CharField(
        required=True,
        help_text='Name of the network'
    )
    cidr = serializers.CharField(
        required=True,
        help_text='CIDR range for the network (e.g., 192.168.100.0/24)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Description of the network'
    )
    is_primary = serializers.BooleanField(
        required=False,
        default=False,
        help_text='Whether this is the primary network for the organization'
    )

    class Meta:
        model = Network
        fields = (
            'id', 'organization', 'name', 'cidr',
            'description', 'is_primary',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        data = super().validate(data)
        print(f"NetworkSerializer validate data: {data}")
        
        # Validate CIDR
        from ..models.network import validate_cidr
        try:
            validate_cidr(data.get('cidr'))
        except Exception as e:
            raise serializers.ValidationError({'cidr': str(e)})
        
        # Check for primary network if this is marked as primary
        if data.get('is_primary'):
            organization_id = self.context.get('organization_id')
            if not organization_id:
                raise serializers.ValidationError('Organization ID is required')
                
            # Check for existing primary network, excluding the current instance if it exists
            existing_primary = Network.objects.filter(
                organization_id=organization_id,
                is_primary=True
            )
            
            # If we're updating an existing network, exclude it from the check
            if self.instance:
                existing_primary = existing_primary.exclude(id=self.instance.id)
                
            if existing_primary.exists():
                raise serializers.ValidationError(
                    'Organization already has a primary network'
                )
        return data

    def create(self, validated_data):
        print(f"NetworkSerializer create validated_data: {validated_data}")
        organization_id = self.context.get('organization_id')
        if not organization_id:
            raise serializers.ValidationError('Organization ID is required')
        validated_data['organization_id'] = organization_id
        
        # Run model validation before creating
        from django.core.exceptions import ValidationError
        try:
            network = Network(**validated_data)
            network.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
            
        return super().create(validated_data)


class FirewallRuleSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SecurityGroup.objects.all(),
        required=False
    )

    class Meta:
        model = FirewallRule
        fields = ['id', 'rule_type', 'protocol', 'port', 'host', 'cidr', 'local_cidr', 'group', 'groups', 'ca_name', 'ca_sha']
        read_only_fields = ['id']

    def validate(self, data):
        # Validate that at least one of host, cidr, group, or groups is specified
        if not any([data.get('host'), data.get('cidr'), data.get('group'), data.get('groups')]):
            raise serializers.ValidationError('At least one of host, cidr, group, or groups must be specified')

        # Validate that only one of host, cidr, group, or groups is specified
        specified_fields = sum([bool(data.get('host')), bool(data.get('cidr')), bool(data.get('group')), bool(data.get('groups'))])
        if specified_fields > 1:
            raise serializers.ValidationError('Only one of host, cidr, group, or groups can be specified')

        # Validate CIDR notation if specified
        if data.get('cidr'):
            try:
                IPv4Network(data['cidr'])
            except ValueError:
                raise serializers.ValidationError('Invalid CIDR notation')

        # Validate local_cidr if specified
        if data.get('local_cidr'):
            try:
                IPv4Network(data['local_cidr'])
            except ValueError:
                raise serializers.ValidationError('Invalid local CIDR notation')

        # Validate port format
        port = data.get('port')
        if port and port != 'any':
            if '-' in port:
                # Validate port range
                try:
                    start, end = map(int, port.split('-'))
                    if not (1 <= start <= 65535 and 1 <= end <= 65535 and start <= end):
                        raise ValueError
                except ValueError:
                    raise serializers.ValidationError('Invalid port range format. Use "start-end" where 1 <= start <= end <= 65535')
            else:
                # Validate single port
                try:
                    port_num = int(port)
                    if not (1 <= port_num <= 65535):
                        raise ValueError
                except ValueError:
                    raise serializers.ValidationError('Port must be between 1 and 65535')

        # Validate that port is not specified for ICMP
        if data.get('protocol') == 'icmp' and port is not None:
            raise serializers.ValidationError('Port should not be specified for ICMP protocol')

        # Validate that port is specified for non-ICMP protocols unless it's "any"
        if data.get('protocol') != 'icmp' and port is None:
            raise serializers.ValidationError('Port is required for non-ICMP protocols')

        return data


class SecurityGroupSerializer(OrganizationScopedSerializer):
    """Serializer for SecurityGroup model."""
    firewall_rules = FirewallRuleSerializer(many=True, read_only=True)
    nodes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    lighthouses = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    firewall_rule_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    node_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    lighthouse_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = SecurityGroup
        fields = ['id', 'organization', 'name', 'description', 'firewall_rules', 
                 'firewall_rule_ids', 'node_ids', 'lighthouse_ids', 'nodes', 'lighthouses']
        read_only_fields = ['id', 'organization']

    def validate(self, data):
        """Validate the data."""
        data = super().validate(data)
        print(f"SecurityGroupSerializer validate data: {data}")
        
        # Get organization from context
        organization_id = self.context.get('organization_id')
        if not organization_id:
            raise serializers.ValidationError("Organization ID is required in context")
            
        # Validate nodes if provided
        if 'node_ids' in data:
            from ..models import Node
            try:
                nodes = Node.objects.filter(
                    id__in=data['node_ids'],
                    organization_id=organization_id
                )
                if nodes.count() != len(data['node_ids']):
                    raise serializers.ValidationError("One or more nodes not found or do not belong to the organization")
            except Exception as e:
                raise serializers.ValidationError(f"Error validating nodes: {str(e)}")
                
        # Validate lighthouses if provided
        if 'lighthouse_ids' in data:
            from ..models import Lighthouse
            try:
                lighthouses = Lighthouse.objects.filter(
                    id__in=data['lighthouse_ids'],
                    organization_id=organization_id
                )
                if lighthouses.count() != len(data['lighthouse_ids']):
                    raise serializers.ValidationError("One or more lighthouses not found or do not belong to the organization")
            except Exception as e:
                raise serializers.ValidationError(f"Error validating lighthouses: {str(e)}")
                
        # Validate firewall rules if provided
        if 'firewall_rule_ids' in data:
            from ..models import FirewallRule
            try:
                rules = FirewallRule.objects.filter(
                    id__in=data['firewall_rule_ids'],
                    security_group__organization_id=organization_id
                )
                if rules.count() != len(data['firewall_rule_ids']):
                    raise serializers.ValidationError("One or more firewall rules not found or do not belong to the organization")
            except Exception as e:
                raise serializers.ValidationError(f"Error validating firewall rules: {str(e)}")
                
        return data

    def create(self, validated_data):
        """Create a new security group."""
        print(f"SecurityGroupSerializer create validated_data: {validated_data}")
        
        # Remove write-only fields
        firewall_rule_ids = validated_data.pop('firewall_rule_ids', [])
        node_ids = validated_data.pop('node_ids', [])
        lighthouse_ids = validated_data.pop('lighthouse_ids', [])
        
        # Get organization from context
        organization_id = self.context.get('organization_id')
        if not organization_id:
            raise serializers.ValidationError("Organization ID is required in context")
            
        # Create the security group
        security_group = SecurityGroup.objects.create(
            organization_id=organization_id,
            name=validated_data.get('name'),
            description=validated_data.get('description', '')
        )
        
        # Add firewall rules
        if firewall_rule_ids:
            from ..models import FirewallRule
            rules = FirewallRule.objects.filter(id__in=firewall_rule_ids)
            security_group.firewall_rules.set(rules)
            
        # Add nodes
        if node_ids:
            from ..models import Node
            nodes = Node.objects.filter(id__in=node_ids)
            security_group.nodes.set(nodes)
            
        # Add lighthouses
        if lighthouse_ids:
            from ..models import Lighthouse
            lighthouses = Lighthouse.objects.filter(id__in=lighthouse_ids)
            security_group.lighthouses.set(lighthouses)
            
        return security_group

    def update(self, instance, validated_data):
        """Update a security group."""
        print(f"SecurityGroupSerializer update validated_data: {validated_data}")
        
        # Remove write-only fields
        firewall_rule_ids = validated_data.pop('firewall_rule_ids', None)
        node_ids = validated_data.pop('node_ids', None)
        lighthouse_ids = validated_data.pop('lighthouse_ids', None)
        
        # Update basic fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        
        # Update firewall rules if provided
        if firewall_rule_ids is not None:
            from ..models import FirewallRule
            rules = FirewallRule.objects.filter(id__in=firewall_rule_ids)
            instance.firewall_rules.set(rules)
            
        # Update nodes if provided
        if node_ids is not None:
            from ..models import Node
            nodes = Node.objects.filter(id__in=node_ids)
            instance.nodes.set(nodes)
            
        # Update lighthouses if provided
        if lighthouse_ids is not None:
            from ..models import Lighthouse
            lighthouses = Lighthouse.objects.filter(id__in=lighthouse_ids)
            instance.lighthouses.set(lighthouses)
            
        return instance


class BaseNodeSerializer(OrganizationScopedSerializer):
    certificate = CertificateSerializer(read_only=True)
    security_groups = SecurityGroupSerializer(many=True, read_only=True)
    security_group_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    def get_fields(self):
        fields = super().get_fields()
        # Set context for child serializers if they support it
        for field_name, field in fields.items():
            if hasattr(field, 'context') and not isinstance(field, serializers.SerializerMethodField):
                try:
                    field.context = self.context
                except AttributeError:
                    # Skip if the field doesn't allow setting context (e.g., read-only serializers)
                    pass
        return fields

    class Meta:
        abstract = True
        fields = (
            'id', 'organization', 'name', 'hostname', 'nebula_ip',
            'certificate', 'security_groups', 'security_group_ids',
            'network', 'created_at', 'updated_at', 'config'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'config')

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
        instance = super().create(validated_data)
        if security_group_ids:
            instance.security_groups.set(security_group_ids)
        return instance

    def update(self, instance, validated_data):
        security_group_ids = validated_data.pop('security_group_ids', None)
        instance = super().update(instance, validated_data)
        if security_group_ids is not None:
            instance.security_groups.set(security_group_ids)
        return instance


class NodeSerializer(BaseNodeSerializer):
    api_key = serializers.SerializerMethodField()

    class Meta(BaseNodeSerializer.Meta):
        model = Node
        fields = BaseNodeSerializer.Meta.fields + ('lighthouse', 'api_key')

    def get_api_key(self, obj):
        # Get the most recent active API key for this node
        api_key = obj.api_keys.filter(is_active=True).order_by('-created_at').first()
        return api_key.key_hash if api_key else None

    def validate(self, data):
        data = super().validate(data)
        if 'network' not in data or data['network'] is None:
            # Get organization from context
            organization_id = self.context.get('organization_id')
            if not organization_id:
                raise serializers.ValidationError('Organization context is required')
            
            # Get or create primary network
            primary_network = Network.objects.filter(
                organization_id=organization_id,
                is_primary=True
            ).first()
            
            if not primary_network:
                # Create primary network if it doesn't exist
                primary_network = Network.objects.create(
                    organization_id=organization_id,
                    name='Primary Network',
                    cidr='192.168.100.0/24',
                    is_primary=True
                )
            
            data['network'] = primary_network

        # Handle duplicate node names
        if 'name' in data:
            base_name = data['name']
            counter = 1
            while Node.objects.filter(
                organization=data.get('organization'),
                name=data['name']
            ).exists():
                data['name'] = f"{base_name}-{counter}"
                counter += 1

        return data

    def create(self, validated_data):
        # Create the node
        instance = super().create(validated_data)

        # Generate certificate
        ca = instance.organization.certificate_authority
        if not ca:
            print("Warning: No CA found for organization. Node created without certificate.")
            return instance

        try:
            certificate = generate_node_certificate(instance, ca)
            instance.certificate = certificate
            instance.save()

            # Generate configuration
            lighthouses = Lighthouse.objects.filter(
                organization=instance.organization,
                network=instance.network,
                is_active=True
            )
            instance.config = generate_node_config(instance, lighthouses)
            instance.save()

            # Generate API key
            key = secrets.token_urlsafe(32)
            api_key = APIKey.objects.create(
                name=f"{instance.name} API Key",
                key_hash=key,
                entity_type=APIKey.EntityTypes.NODE,
                node=instance
            )
            self.api_key = key  # Store the key to return in response

        except Exception as e:
            print(f"Warning: Failed to generate certificate, config, or API key: {str(e)}")
            # Don't raise the error, just return the instance without cert/config/key

        return instance


class LighthouseSerializer(BaseNodeSerializer):
    api_key = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"LighthouseSerializer init context: {self.context}")
        print(f"LighthouseSerializer init organization_id: {self.context.get('organization_id')}")

    class Meta:
        model = Lighthouse
        fields = (
            'id', 'organization', 'name', 'hostname', 'nebula_ip',
            'certificate', 'security_groups', 'security_group_ids',
            'network', 'public_ip', 'port', 'is_active', 'last_check_in',
            'config', 'created_at', 'updated_at', 'api_key'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_check_in')
        extra_kwargs = {
            'organization': {'write_only': True},
            'network': {'write_only': True}
        }

    def get_api_key(self, obj):
        """Get the most recent active API key for the lighthouse."""
        # First check if the API key is stored in the serializer
        if hasattr(self, '_api_key'):
            return self._api_key
        # Then check if it's stored in the instance
        if hasattr(obj, '_api_key'):
            return obj._api_key
        # Finally, try to get it from the database
        api_key = obj.api_keys.filter(is_active=True).order_by('-created_at').first()
        return api_key.key_hash if api_key else None

    def validate(self, data):
        print(f"LighthouseSerializer validate context: {self.context}")
        print(f"LighthouseSerializer validate data: {data}")
        
        # Get organization from context
        organization_id = self.context.get('organization_id')
        if not organization_id:
            raise serializers.ValidationError('Organization context is required')
        
        # If network is not provided, get or create primary network
        if 'network' not in data or data['network'] is None:
            primary_network = Network.objects.filter(
                organization_id=organization_id,
                is_primary=True
            ).first()
            
            if not primary_network:
                # Create primary network if it doesn't exist
                primary_network = Network.objects.create(
                    organization_id=organization_id,
                    name='Primary Network',
                    cidr='192.168.100.0/24',
                    is_primary=True
                )
            
            data['network'] = primary_network
        
        # Ensure network belongs to the organization
        if isinstance(data['network'], Network):
            network_org_id = str(data['network'].organization_id)
        else:
            network = Network.objects.get(id=data['network'])
            network_org_id = str(network.organization_id)
            
        if network_org_id != str(organization_id):
            raise serializers.ValidationError('Network must belong to the same organization')
        
        # Handle duplicate lighthouse names
        if 'name' in data:
            base_name = data['name']
            counter = 1
            while Lighthouse.objects.filter(
                organization_id=organization_id,
                name=data['name']
            ).exists():
                data['name'] = f"{base_name}-{counter}"
                counter += 1
        
        # Add organization_id to data
        data['organization_id'] = organization_id
        
        return data

    def create(self, validated_data):
        print(f"LighthouseSerializer create validated_data: {validated_data}")
        
        # Create the lighthouse using the parent class's create method
        instance = super().create(validated_data)
        print(f"LighthouseSerializer created instance: {instance}")

        try:
            # Generate certificate
            ca = instance.organization.certificate_authority
            if not ca:
                print("Warning: No CA found for organization. Lighthouse created without certificate.")
                return instance

            certificate = generate_lighthouse_certificate(instance, ca)
            instance.certificate = certificate
            instance.save()

            # Generate configuration
            instance.config = generate_lighthouse_config(instance)
            instance.save()

            # Generate API key
            key = secrets.token_urlsafe(32)
            api_key = APIKey.objects.create(
                name=f"{instance.name} API Key",
                key_hash=key,
                entity_type=APIKey.EntityTypes.LIGHTHOUSE,
                lighthouse=instance
            )
            # Store the key in the instance's context
            instance._api_key = key
            self._api_key = key  # Also store in serializer for backwards compatibility

            return instance

        except Exception as e:
            print(f"Warning: Failed to generate certificate, config, or API key: {str(e)}")
            # Don't raise the error, just return the instance without cert/config/key
            return instance

    def to_representation(self, instance):
        """Override to include the API key in the response."""
        ret = super().to_representation(instance)
        if hasattr(self, '_api_key'):
            ret['api_key'] = self._api_key
        return ret 