"""
Signal handlers for the Simple Nebula API.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import APIKey, Certificate, CertificateAuthority, Membership

# List of user emails that should always be admins
ADMIN_EMAILS = ['myadminemail@gmail.com']

@receiver(post_save, sender=CertificateAuthority)
def handle_ca_expiration(sender, instance, created, **kwargs):
    """Handle CA certificate expiration."""
    if not created and instance.expires_at <= timezone.now():
        # TODO: Implement CA expiration handling
        pass


@receiver(post_save, sender=Certificate)
def handle_cert_expiration(sender, instance, created, **kwargs):
    """Handle certificate expiration."""
    if not created and instance.expires_at <= timezone.now():
        # TODO: Implement certificate expiration handling
        pass


@receiver(post_save, sender=APIKey)
def handle_api_key_expiration(sender, instance, created, **kwargs):
    """Handle API key expiration."""
    if not created and instance.expires_at and instance.expires_at <= timezone.now():
        instance.is_active = False
        instance.save(update_fields=['is_active'])


@receiver(post_save, sender=Membership)
def ensure_admin_role(sender, instance, created, **kwargs):
    """
    Signal handler to ensure specific users are always assigned admin role
    when added to an organization.
    """
    if instance.user.email in ADMIN_EMAILS and instance.role != Membership.Roles.ADMIN:
        instance.role = Membership.Roles.ADMIN
        # Use update to prevent calling post_save again
        Membership.objects.filter(id=instance.id).update(role=Membership.Roles.ADMIN) 