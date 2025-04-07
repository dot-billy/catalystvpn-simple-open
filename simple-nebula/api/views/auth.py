from rest_framework import viewsets, status, generics, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from ..models import Organization, Membership, Network
from ..serializers import (
    UserSerializer, UserCreateSerializer,
    OrganizationSerializer, MembershipSerializer
)
from ..permissions import IsOrganizationAdmin
from .base import OrganizationScopedViewSet
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound, PermissionDenied

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """Serializer for login endpoint."""
    email = serializers.EmailField(
        required=True,
        help_text='Email address for authentication'
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text='Password for authentication'
    )


class LoginView(generics.GenericAPIView):
    """View for user login."""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        summary='User login',
        description='Authenticate user and return JWT tokens',
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description='Successfully authenticated',
                response=UserSerializer
            ),
            401: OpenApiResponse(description='Invalid credentials'),
            400: OpenApiResponse(description='Invalid input')
        },
        tags=['authentication']
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(email=email, password=password)

        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh endpoint."""
    refresh = serializers.CharField(
        required=True,
        help_text='Refresh token for obtaining a new access token'
    )


class RefreshTokenView(generics.GenericAPIView):
    """View for refreshing JWT tokens."""
    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer

    @extend_schema(
        summary='Refresh JWT token',
        description='Get a new access token using a refresh token',
        request=RefreshTokenSerializer,
        responses={
            200: OpenApiResponse(
                description='Successfully refreshed token',
                response=RefreshTokenSerializer
            ),
            401: OpenApiResponse(description='Invalid refresh token'),
            400: OpenApiResponse(description='Invalid input')
        },
        tags=['authentication']
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data['refresh']
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        except TokenError:
            return Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing organizations.
    
    Organizations are the top-level entities in the system that group related resources
    such as networks, lighthouses, and nodes. Each organization has its own:
    - Certificate Authority
    - Primary Network
    - Security Groups
    - Lighthouses
    - Nodes
    - Members
    
    Operations:
    - List organizations the user has access to
    - Create a new organization with a primary network
    - Retrieve organization details
    - Update organization information
    - Delete an organization (requires admin access)
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        """Get organizations the user has access to."""
        return self.queryset.filter(users=self.request.user).prefetch_related(
            'certificate_authority',
            'memberships',
            'memberships__user',
            'lighthouse_set',
            'node_set'
        )

    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        """
        Create a new organization with a primary network.
        
        This endpoint creates:
        1. A new organization
        2. A primary network for the organization
        3. A certificate authority for the organization
        4. An admin membership for the requesting user
        
        The organization will be created with:
        - A unique slug derived from the name
        - A primary network with the specified CIDR
        - A certificate authority for managing device certificates
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(f"Failed to create organization: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MembershipViewSet(OrganizationScopedViewSet):
    queryset = Membership.objects.select_related('user', 'organization')
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]

    def get_organization_id(self):
        """Get organization ID from URL kwargs."""
        # Try organization_id first (from nested router)
        organization_id = self.kwargs.get('organization_id') or self.kwargs.get('organization_pk')
        if organization_id:
            print(f"MembershipViewSet get_organization_id: {organization_id} from organization_id")
            return str(organization_id)
        # Try organization_slug (from organization lookup)
        organization_slug = self.kwargs.get('organization_slug')
        if organization_slug:
            print(f"MembershipViewSet get_organization_id: slug {organization_slug}")
            from ..models import Organization
            try:
                organization = Organization.objects.get(slug=organization_slug)
                print(f"MembershipViewSet get_organization_id: found by slug {organization.id}")
                return str(organization.id)
            except Organization.DoesNotExist:
                print(f"MembershipViewSet get_organization_id: not found by slug {organization_slug}")
                return None
        print(f"MembershipViewSet get_organization_id: not found in {self.kwargs}")
        return None

    def get_queryset(self):
        organization_id = self.get_organization_id()
        if not organization_id:
            print(f"MembershipViewSet get_queryset: no organization_id")
            return self.queryset.none()
        print(f"MembershipViewSet get_queryset: filtering by organization_id {organization_id}")
        return self.queryset.filter(organization_id=organization_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        organization_id = self.get_organization_id()
        print(f"MembershipViewSet serializer context: organization_id {organization_id}")
        context['organization_id'] = organization_id
        return context

    def perform_create(self, serializer):
        organization_id = self.get_organization_id()
        if not organization_id:
            print(f"MembershipViewSet perform_create: no organization_id")
            raise ValidationError("Organization not found")
        
        from ..models import Organization
        try:
            organization = Organization.objects.get(id=organization_id)
            print(f"MembershipViewSet perform_create: found organization {organization.id}")
            serializer.save(organization=organization)
        except Organization.DoesNotExist:
            print(f"MembershipViewSet perform_create: organization not found {organization_id}")
            raise ValidationError("Organization not found")


class RolesViewSet(viewsets.ViewSet):
    """
    API endpoint for retrieving available roles in the system.
    
    This endpoint allows clients to retrieve information about the available roles
    that can be assigned to users within organizations.
    
    Operations:
    - List all available roles
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary='List available roles',
        description='Get a list of all available roles that can be assigned to users within organizations',
        responses={
            200: OpenApiResponse(
                description='List of available roles',
                response=serializers.ListSerializer(child=serializers.DictField())
            )
        },
        tags=['authentication']
    )
    def list(self, request):
        """
        Return a list of all available roles.
        """
        roles = [
            {'id': role_id, 'name': role_name}
            for role_id, role_name in Membership.Roles.choices
        ]
        return Response(roles) 