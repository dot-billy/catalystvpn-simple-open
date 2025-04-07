from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    UserViewSet, OrganizationViewSet, MembershipViewSet,
    CertificateAuthorityViewSet, CertificateViewSet,
    SecurityGroupViewSet, NodeViewSet, LighthouseViewSet,
    APIKeyViewSet, NetworkViewSet, auth, network
)
from .views.auth import RolesViewSet

# Create a router for top-level resources
router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('organizations', OrganizationViewSet, basename='organizations')
router.register('memberships', MembershipViewSet, basename='memberships')
router.register('nodes', NodeViewSet, basename='nodes')
router.register('lighthouses', LighthouseViewSet, basename='lighthouses')
router.register('roles', RolesViewSet, basename='roles')

# Create nested routers for organization-scoped resources
org_router = routers.NestedSimpleRouter(router, 'organizations', lookup='organization')
org_router.register('members', MembershipViewSet, basename='organization-members')
org_router.register('ca', CertificateAuthorityViewSet, basename='organization-ca')
org_router.register('certificates', CertificateViewSet, basename='organization-certificates')
org_router.register('networks', NetworkViewSet, basename='organization-networks')
org_router.register('security-groups', SecurityGroupViewSet, basename='organization-security-groups')
org_router.register('nodes', NodeViewSet, basename='organization-nodes')
org_router.register('lighthouses', LighthouseViewSet, basename='organization-lighthouses')
org_router.register('api-keys', APIKeyViewSet, basename='organization-api-keys')

# Register device update endpoints
router.register('device/updates', network.DeviceUpdateViewSet, basename='device-updates')

# Add tags to the router for Swagger documentation
router.tags = ['organizations', 'users', 'networks', 'devices', 'roles']
org_router.tags = ['organization-resources']

urlpatterns = [
    path('', include(router.urls)),
    path('', include(org_router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('token/', auth.LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', auth.RefreshTokenView.as_view(), name='token_refresh'),
] 