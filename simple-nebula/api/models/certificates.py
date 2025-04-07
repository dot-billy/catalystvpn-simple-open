import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError


class CertificateAuthority(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(
        'Organization',
        on_delete=models.CASCADE,
        related_name='certificate_authority'
    )
    network = models.ForeignKey(
        'Network',
        on_delete=models.PROTECT,
        related_name='certificate_authority',
        limit_choices_to={'is_primary': True}
    )
    ca_cert = models.TextField(_('CA certificate'))
    ca_key = models.TextField(_('CA private key'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    expires_at = models.DateTimeField(_('expires at'))
    revoked = models.BooleanField(_('revoked'), default=False)
    revoked_at = models.DateTimeField(_('revoked at'), null=True, blank=True)

    class Meta:
        verbose_name = _('certificate authority')
        verbose_name_plural = _('certificate authorities')

    def __str__(self):
        return f'CA for {self.organization}'

    def clean(self):
        if self.network and self.network.organization != self.organization:
            raise ValidationError('Network must belong to the same organization')
        if self.network and not self.network.is_primary:
            raise ValidationError('Network must be marked as primary')


class Certificate(models.Model):
    class CertificateTypes(models.TextChoices):
        NODE = 'node', _('Node')
        LIGHTHOUSE = 'lighthouse', _('Lighthouse')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ca = models.ForeignKey(
        CertificateAuthority,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    cert_type = models.CharField(
        _('certificate type'),
        max_length=20,
        choices=CertificateTypes.choices
    )
    cert = models.TextField(_('certificate'))
    key = models.TextField(_('private key'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    expires_at = models.DateTimeField(_('expires at'))
    revoked = models.BooleanField(_('revoked'), default=False)
    revoked_at = models.DateTimeField(_('revoked at'), null=True, blank=True)
    nebula_ip = models.GenericIPAddressField(_('Nebula IP'), protocol='IPv4')

    class Meta:
        verbose_name = _('certificate')
        verbose_name_plural = _('certificates')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.cert_type} cert for {self.nebula_ip}' 