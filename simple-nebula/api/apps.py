"""
API app configuration for Simple Nebula.
"""
from django.apps import AppConfig


class APIConfig(AppConfig):
    """Configuration for the API app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """Import signals when the app is ready."""
        import api.signals  # noqa
