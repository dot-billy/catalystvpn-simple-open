from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import APIKey
from ..serializers import APIKeySerializer
from .base import OrganizationOperatorViewSet


class APIKeyViewSet(OrganizationOperatorViewSet):
    queryset = APIKey.objects.select_related('node', 'lighthouse')
    serializer_class = APIKeySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        entity_type = self.request.query_params.get('entity_type')
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        return queryset

    @action(detail=True, methods=['post'])
    def revoke(self, request, organization_id=None, pk=None):
        """Revoke an API key."""
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save()
        return Response({'status': 'API key revoked'})

    @action(detail=True, methods=['post'])
    def regenerate(self, request, organization_id=None, pk=None):
        """Regenerate an API key."""
        api_key = self.get_object()
        # TODO: Implement key regeneration logic
        return Response({'status': 'API key regenerated'}) 