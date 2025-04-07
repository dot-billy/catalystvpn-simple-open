from django.utils import timezone
from rest_framework import authentication
from rest_framework import exceptions
from .models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None

        try:
            key = APIKey.objects.select_related('node', 'lighthouse').get(
                key_hash=api_key,
                is_active=True
            )

            # Update last used timestamp
            key.last_used = timezone.now()
            key.save(update_fields=['last_used'])

            # Check if key has expired
            if key.expires_at and key.expires_at <= timezone.now():
                raise exceptions.AuthenticationFailed('API key has expired')

            # Return the associated entity (node or lighthouse)
            entity = key.node or key.lighthouse
            return (entity, key)

        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key') 