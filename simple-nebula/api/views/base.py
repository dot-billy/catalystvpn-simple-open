from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsOrganizationMember, IsOrganizationOperator


class OrganizationScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get_organization_id(self):
        """Get organization ID from URL kwargs."""
        # Try organization_id first (from nested router)
        organization_id = self.kwargs.get('organization_id') or self.kwargs.get('organization_pk')
        print(f"get_organization_id kwargs: {self.kwargs}")
        print(f"get_organization_id organization_id: {organization_id}")
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
        organization_id = self.get_organization_id()
        print(f"Getting queryset for organization {organization_id}")
        return self.queryset.filter(organization_id=organization_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        organization_id = self.get_organization_id()
        print(f"OrganizationScopedViewSet context organization_id: {organization_id}")
        context['organization_id'] = organization_id
        context['request'] = self.request
        return context


class OrganizationOperatorViewSet(OrganizationScopedViewSet):
    permission_classes = [IsAuthenticated, IsOrganizationOperator]


class ReadOnlyOrganizationViewSet(mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin,
                                 viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        organization_id = self.kwargs.get('organization_pk') or self.kwargs.get('organization_id')
        return self.queryset.filter(organization_id=organization_id) 