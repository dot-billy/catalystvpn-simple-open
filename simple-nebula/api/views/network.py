from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import SecurityGroup, Node, Lighthouse, Network, FirewallRule
from ..serializers.network import (
    SecurityGroupSerializer, NodeSerializer, LighthouseSerializer,
    NetworkSerializer, FirewallRuleSerializer
)
from .base import OrganizationScopedViewSet, OrganizationOperatorViewSet
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ..authentication import APIKeyAuthentication
from ..permissions import IsOrganizationOperator, IsDeviceAuthenticated, IsOrganizationViewer


class NetworkViewSet(OrganizationScopedViewSet):
    """
    API endpoints for managing organization networks.
    
    Networks are used to define IP ranges and manage device connectivity within an organization.
    Each organization has a primary network created automatically, and additional networks
    can be created as needed.
    
    Operations:
    - List networks in an organization
    - Create a new network
    - Retrieve network details
    - Update network information
    - Delete a network
    - Get available IPs in a network
    """
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOrganizationOperator]
        else:
            permission_classes = [IsAuthenticated, IsOrganizationViewer]
        return [permission() for permission in permission_classes]

    def get_organization_id(self):
        """Get organization ID from URL kwargs."""
        # Try organization_id first (from nested router)
        organization_id = self.kwargs.get('organization_id') or self.kwargs.get('organization_pk')
        if organization_id:
            return str(organization_id)
        # Try organization_slug (from organization lookup)
        organization_slug = self.kwargs.get('organization_slug')
        if organization_slug:
            from ..models import Organization
            try:
                organization = Organization.objects.get(slug=organization_slug)
                return str(organization.id)
            except Organization.DoesNotExist:
                return None
        return None

    def get_queryset(self):
        """Get networks for the current organization."""
        organization_id = self.get_organization_id()
        if not organization_id:
            return Network.objects.none()
        return super().get_queryset().filter(organization_id=organization_id)

    def get_serializer_context(self):
        """Add organization context to serializer."""
        context = super().get_serializer_context()
        context['organization_id'] = self.get_organization_id()
        return context

    @action(detail=True, methods=['get'])
    def available_ips(self, request, organization_id=None, pk=None):
        """
        Get list of available IPs in this network.
        
        This endpoint returns the next available IP address that can be assigned
        to a device in this network.
        """
        network = self.get_object()
        try:
            available_ip = network.get_available_ip()
            return Response({'available_ip': available_ip})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SecurityGroupViewSet(OrganizationScopedViewSet):
    queryset = SecurityGroup.objects.all()
    serializer_class = SecurityGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_organization_id(self):
        """Get organization ID from URL kwargs."""
        # Try organization_id first (from nested router)
        organization_id = self.kwargs.get('organization_id') or self.kwargs.get('organization_pk')
        if organization_id:
            return str(organization_id)
        # Try organization_slug (from organization lookup)
        organization_slug = self.kwargs.get('organization_slug')
        if organization_slug:
            from ..models import Organization
            try:
                organization = Organization.objects.get(slug=organization_slug)
                return str(organization.id)
            except Organization.DoesNotExist:
                return None
        return None

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOrganizationOperator]
        else:
            permission_classes = [IsAuthenticated, IsOrganizationViewer]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        organization_id = self.get_organization_id()
        print(f"SecurityGroupViewSet get_queryset organization_id: {organization_id}")
        return super().get_queryset().prefetch_related('firewall_rules', 'nodes', 'lighthouses')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        organization_id = self.get_organization_id()
        print(f"SecurityGroupViewSet get_serializer_context organization_id: {organization_id}")
        context['organization_id'] = organization_id
        return context

    @action(detail=True, methods=['post'])
    def add_rule(self, request, organization_slug=None, pk=None):
        """Add a firewall rule to the security group."""
        security_group = self.get_object()
        
        # Verify organization consistency
        if security_group.organization.slug != organization_slug:
            return Response(
                {"error": "Security group does not belong to the specified organization"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a mutable copy of the request data
        data = request.data.copy()
        
        serializer = FirewallRuleSerializer(data=data)
        if serializer.is_valid():
            # Save the rule with the security group
            serializer.save(security_group=security_group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_rule(self, request, pk=None):
        security_group = self.get_object()
        rule_id = request.data.get('rule_id')
        if not rule_id:
            return Response(
                {'detail': 'rule_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            rule = security_group.firewall_rules.get(id=rule_id)
            rule.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FirewallRule.DoesNotExist:
            return Response(
                {'detail': 'Rule not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def add_nodes(self, request, organization_slug=None, pk=None):
        security_group = self.get_object()
        node_ids = request.data.get('node_ids', [])
        if not node_ids:
            return Response(
                {'detail': 'node_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            nodes = Node.objects.filter(id__in=node_ids, organization=security_group.organization)
            if nodes.count() != len(node_ids):
                return Response(
                    {'detail': 'One or more nodes not found or do not belong to this organization'},
                    status=status.HTTP_404_NOT_FOUND
                )
            security_group.nodes.add(*nodes)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['delete'])
    def remove_nodes(self, request, pk=None):
        security_group = self.get_object()
        node_ids = request.data.get('node_ids', [])
        if not node_ids:
            return Response(
                {'detail': 'node_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        security_group.nodes.remove(*node_ids)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def add_lighthouses(self, request, organization_slug=None, pk=None):
        security_group = self.get_object()
        lighthouse_ids = request.data.get('lighthouse_ids', [])
        if not lighthouse_ids:
            return Response(
                {'detail': 'lighthouse_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            lighthouses = Lighthouse.objects.filter(id__in=lighthouse_ids, organization=security_group.organization)
            if lighthouses.count() != len(lighthouse_ids):
                return Response(
                    {'detail': 'One or more lighthouses not found or do not belong to this organization'},
                    status=status.HTTP_404_NOT_FOUND
                )
            security_group.lighthouses.add(*lighthouses)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['delete'])
    def remove_lighthouses(self, request, pk=None):
        security_group = self.get_object()
        lighthouse_ids = request.data.get('lighthouse_ids', [])
        if not lighthouse_ids:
            return Response(
                {'detail': 'lighthouse_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        security_group.lighthouses.remove(*lighthouse_ids)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NodeViewSet(OrganizationOperatorViewSet):
    queryset = Node.objects.select_related('certificate', 'lighthouse', 'network')
    serializer_class = NodeSerializer

    def get_organization_id(self):
        """Get organization ID from URL kwargs."""
        # Try organization_id first (from nested router)
        organization_id = self.kwargs.get('organization_id') or self.kwargs.get('organization_pk')
        if organization_id:
            return str(organization_id)
        # Try organization_slug (from organization lookup)
        organization_slug = self.kwargs.get('organization_slug')
        if organization_slug:
            from ..models import Organization
            try:
                organization = Organization.objects.get(slug=organization_slug)
                return str(organization.id)
            except Organization.DoesNotExist:
                return None
        return None

    def get_queryset(self):
        """Get nodes for the current organization."""
        organization_id = self.get_organization_id()
        if not organization_id:
            return Node.objects.none()
        return super().get_queryset().filter(organization_id=organization_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Add organization_id and request to context for validation
        context['organization_id'] = self.get_organization_id()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def generate_config(self, request, organization_id=None, pk=None):
        """Generate Nebula configuration for a node."""
        node = self.get_object()
        # TODO: Implement config generation logic
        return Response({'status': 'Configuration generated'})

    @action(detail=True, methods=['post'])
    def check_in(self, request, organization_id=None, pk=None):
        """Handle node check-in."""
        node = self.get_object()
        # TODO: Implement check-in logic
        return Response({'status': 'Check-in successful'})


class LighthouseViewSet(OrganizationScopedViewSet):
    queryset = Lighthouse.objects.select_related('certificate', 'network')
    serializer_class = LighthouseSerializer
    permission_classes = [IsAuthenticated]

    def get_organization_id(self):
        """Get organization ID from URL kwargs."""
        # Try organization_id first (from nested router)
        organization_id = self.kwargs.get('organization_id') or self.kwargs.get('organization_pk')
        if organization_id:
            return str(organization_id)
        # Try organization_slug (from organization lookup)
        organization_slug = self.kwargs.get('organization_slug')
        if organization_slug:
            from ..models import Organization
            try:
                organization = Organization.objects.get(slug=organization_slug)
                return str(organization.id)
            except Organization.DoesNotExist:
                return None
        return None

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOrganizationOperator]
        else:
            permission_classes = [IsAuthenticated, IsOrganizationViewer]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Add organization_id and request to context for validation
        organization_id = self.get_organization_id()
        context['organization_id'] = organization_id
        context['request'] = self.request
        print(f"LighthouseViewSet get_serializer_context: {context}")
        return context

    def create(self, request, *args, **kwargs):
        print(f"LighthouseViewSet create request data: {request.data}")
        organization_id = self.get_organization_id()
        print(f"LighthouseViewSet create organization_id: {organization_id}")
        
        # Get the serializer with the proper context
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the instance
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        
        # Get the API key from the instance
        api_key = getattr(instance, '_api_key', None)
        if api_key:
            # Create a new dictionary with the serializer data and API key
            response_data = dict(serializer.data)
            response_data['api_key'] = api_key
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def generate_config(self, request, organization_id=None, pk=None):
        """Generate Nebula configuration for a lighthouse."""
        lighthouse = self.get_object()
        # TODO: Implement config generation logic
        return Response({'status': 'Configuration generated'})

    @action(detail=True, methods=['post'])
    def check_in(self, request, organization_id=None, pk=None):
        """Handle lighthouse check-in."""
        lighthouse = self.get_object()
        # TODO: Implement check-in logic
        return Response({'status': 'Check-in successful'})

    @action(detail=True, methods=['get'])
    def nodes(self, request, organization_id=None, pk=None):
        """Get nodes connected to this lighthouse."""
        lighthouse = self.get_object()
        nodes = lighthouse.nodes.all()
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)


class DeviceUpdateViewSet(viewsets.ViewSet):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsDeviceAuthenticated]

    def get_object(self):
        # The APIKeyAuthentication will set the entity (node or lighthouse) as the user
        return self.request.user

    @action(detail=False, methods=['get'])
    def check_updates(self, request):
        """Check for configuration updates."""
        device = self.get_object()
        
        # Update last check-in time
        device.last_check_in = timezone.now()
        device.save(update_fields=['last_check_in'])

        # Return the current configuration
        if isinstance(device, Node):
            serializer = NodeSerializer(device)
        else:
            serializer = LighthouseSerializer(device)

        return Response({
            'has_updates': False,  # TODO: Implement update detection logic
            'config': serializer.data.get('config', {}),
            'last_check_in': device.last_check_in
        })

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get device status."""
        device = self.get_object()
        
        return Response({
            'id': device.id,
            'name': device.name,
            'hostname': device.hostname,
            'nebula_ip': device.nebula_ip,
            'is_active': getattr(device, 'is_active', True),
            'last_check_in': device.last_check_in,
            'certificate_expires_at': device.certificate.expires_at if device.certificate else None
        }) 