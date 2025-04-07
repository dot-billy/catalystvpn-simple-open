from rest_framework import permissions
from .models import Membership, Node, Lighthouse


class IsOrganizationMember(permissions.BasePermission):
    def get_organization_id(self, view):
        """Get organization ID from view kwargs."""
        return view.kwargs.get('organization_pk') or view.kwargs.get('organization_id')

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        organization_id = self.get_organization_id(view)
        if not organization_id:
            return False

        return request.user.memberships.filter(
            organization_id=organization_id
        ).exists()


class IsOrganizationAdmin(IsOrganizationMember):
    def get_organization_id(self, view):
        """Get organization ID from view kwargs."""
        # Try organization_id first (from nested router)
        organization_id = view.kwargs.get('organization_id') or view.kwargs.get('organization_pk')
        if organization_id:
            print(f"IsOrganizationAdmin found organization_id in kwargs: {organization_id}")
            return str(organization_id)
        # Try organization_slug (from organization lookup)
        organization_slug = view.kwargs.get('organization_slug')
        if organization_slug:
            print(f"IsOrganizationAdmin found organization_slug in kwargs: {organization_slug}")
            from .models import Organization
            try:
                organization = Organization.objects.get(slug=organization_slug)
                print(f"IsOrganizationAdmin found organization by slug: {organization.id}")
                return str(organization.id)
            except Organization.DoesNotExist:
                print(f"IsOrganizationAdmin organization not found with slug: {organization_slug}")
                return None
        print(f"IsOrganizationAdmin no organization_id or organization_slug found in kwargs: {view.kwargs}")
        return None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            print(f"IsOrganizationAdmin user not authenticated: {request.user}")
            return False

        organization_id = self.get_organization_id(view)
        if not organization_id:
            print(f"IsOrganizationAdmin no organization_id found for view")
            return False

        # For GET requests, allow if user is a member
        if request.method in permissions.SAFE_METHODS:
            is_member = request.user.memberships.filter(
                organization_id=organization_id
            ).exists()
            print(f"IsOrganizationAdmin {'✓' if is_member else '✗'} User {request.user.email} is {'a' if is_member else 'not a'} member of organization {organization_id} (safe method)")
            return is_member

        # For other methods, require admin role
        is_admin = request.user.memberships.filter(
            organization_id=organization_id,
            role=Membership.Roles.ADMIN
        ).exists()
        print(f"IsOrganizationAdmin {'✓' if is_admin else '✗'} User {request.user.email} is {'an' if is_admin else 'not an'} admin of organization {organization_id}")
        
        # Print all memberships for this user to debug
        memberships = request.user.memberships.all()
        print(f"IsOrganizationAdmin user {request.user.email} has {memberships.count()} memberships:")
        for membership in memberships:
            print(f"  - Organization {membership.organization.slug} ({membership.organization.id}): {membership.role}")
            
        return is_admin


class IsOrganizationOperator(IsOrganizationMember):
    def get_organization_id(self, view):
        """Get organization ID from view kwargs."""
        # Try organization_id first (from nested router)
        organization_id = view.kwargs.get('organization_id') or view.kwargs.get('organization_pk')
        if organization_id:
            return str(organization_id)
        # Try organization_slug (from organization lookup)
        organization_slug = view.kwargs.get('organization_slug')
        if organization_slug:
            from .models import Organization
            try:
                organization = Organization.objects.get(slug=organization_slug)
                return str(organization.id)
            except Organization.DoesNotExist:
                return None
        return None

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            print(f"✗ User {request.user.email} is not a member of organization {self.get_organization_id(view)}")
            return False

        organization_id = self.get_organization_id(view)
        print(f"Checking operator permissions for user {request.user.email} in organization {organization_id}")
        
        memberships = request.user.memberships.filter(
            organization_id=organization_id,
            role__in=[Membership.Roles.ADMIN, Membership.Roles.OPERATOR]
        )
        
        has_permission = memberships.exists()
        print(f"{'✓' if has_permission else '✗'} User {request.user.email} has {'operator' if has_permission else 'no operator'} permissions for organization {organization_id}")
        if has_permission:
            membership = memberships.first()
            print(f"  Role: {membership.role}")
        return has_permission


class IsOrganizationViewer(IsOrganizationMember):
    def get_organization_id(self, view):
        """Get organization ID from view kwargs."""
        # Try organization_id first (from nested router)
        organization_id = view.kwargs.get('organization_id') or view.kwargs.get('organization_pk')
        if organization_id:
            print(f"Found organization_id in kwargs: {organization_id}")
            return str(organization_id)
        # Try organization_slug (from organization lookup)
        organization_slug = view.kwargs.get('organization_slug')
        if organization_slug:
            print(f"Found organization_slug in kwargs: {organization_slug}")
            from api.models import Organization
            try:
                organization = Organization.objects.get(slug=organization_slug)
                print(f"Found organization by slug: {organization.id}")
                return str(organization.id)
            except Organization.DoesNotExist:
                print(f"Organization not found with slug: {organization_slug}")
                return None
        print(f"No organization_id or organization_slug found in kwargs: {view.kwargs}")
        return None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            print(f"User not authenticated: {request.user}")
            return False

        organization_id = self.get_organization_id(view)
        if not organization_id:
            print(f"No organization_id found for view")
            return False

        print(f"Checking membership for user {request.user.email} in organization {organization_id}")
        memberships = request.user.memberships.filter(organization_id=organization_id)
        has_membership = memberships.exists()
        print(f"{'✓' if has_membership else '✗'} User {request.user.email} is {'a' if has_membership else 'not a'} member of organization {organization_id}")
        
        if has_membership:
            membership = memberships.first()
            print(f"  Role: {membership.role}")
            if request.method in permissions.SAFE_METHODS:
                print(f"✓ User {request.user.email} has viewer access for organization {organization_id}")
                return True
            else:
                has_operator = membership.role in [Membership.Roles.ADMIN, Membership.Roles.OPERATOR]
                print(f"{'✓' if has_operator else '✗'} User {request.user.email} has {'operator' if has_operator else 'no operator'} permissions for organization {organization_id}")
                return has_operator
        
        return False


class HasAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return False

        # API key validation will be handled in the authentication class
        return True


class IsDeviceAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated devices (nodes or lighthouses).
    """
    def has_permission(self, request, view):
        return bool(request.user and isinstance(request.user, (Node, Lighthouse))) 