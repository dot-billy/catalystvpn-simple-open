"""
Custom token views for Simple Nebula API.
"""
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that uses email instead of username."""
    username_field = 'email'
    email = serializers.EmailField(
        required=True,
        help_text='Email address for authentication'
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text='Password for authentication'
    )

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add any additional validation or data here
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses email instead of username."""
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary='Obtain JWT token pair',
        description='Get access and refresh tokens using email and password',
        responses={
            200: OpenApiResponse(
                description='Successfully obtained token pair',
                response=CustomTokenObtainPairSerializer
            ),
            401: OpenApiResponse(description='Invalid credentials'),
            400: OpenApiResponse(description='Invalid input')
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """Custom token refresh serializer."""
    refresh = serializers.CharField(
        required=True,
        help_text='Refresh token for obtaining a new access token'
    )
    
    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs['refresh'])
            data = {'access': str(refresh.access_token)}
            return data
        except Exception as e:
            raise serializers.ValidationError({'refresh': str(e)})


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view."""
    serializer_class = CustomTokenRefreshSerializer

    @extend_schema(
        summary='Refresh JWT token',
        description='Get a new access token using a refresh token',
        responses={
            200: OpenApiResponse(
                description='Successfully refreshed token',
                response=CustomTokenRefreshSerializer
            ),
            401: OpenApiResponse(description='Invalid refresh token'),
            400: OpenApiResponse(description='Invalid input')
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs) 