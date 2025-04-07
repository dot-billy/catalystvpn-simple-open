import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class APIKey(models.Model):
    class EntityTypes(models.TextChoices):
        NODE = 'node', _('Node')
        LIGHTHOUSE = 'lighthouse', _('Lighthouse')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255)
    key_hash = models.CharField(_('key hash'), max_length=255)
    entity_type = models.CharField(
        _('entity type'),
        max_length=20,
        choices=EntityTypes.choices
    )
    node = models.ForeignKey(
        'Node',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='api_keys'
    )
    lighthouse = models.ForeignKey(
        'Lighthouse',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='api_keys'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True)
    last_used = models.DateTimeField(_('last used'), null=True, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('API key')
        verbose_name_plural = _('API keys')
        ordering = ['-created_at']

    def __str__(self):
        entity = self.node or self.lighthouse
        return f'{self.name} - {entity} ({self.entity_type})'

    def save(self, *args, **kwargs):
        if self.node and self.lighthouse:
            raise ValueError(_('API key can only be associated with either a node or a lighthouse, not both'))
        if not self.node and not self.lighthouse:
            raise ValueError(_('API key must be associated with either a node or a lighthouse'))
        super().save(*args, **kwargs) 