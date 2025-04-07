import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Membership',
        related_name='organizations'
    )

    class Meta:
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')
        ordering = ['name']

    def __str__(self):
        return self.name


class Membership(models.Model):
    class Roles(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        OPERATOR = 'operator', _('Operator')
        VIEWER = 'viewer', _('Viewer')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Roles.choices,
        default=Roles.VIEWER
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')
        unique_together = ('user', 'organization')
        ordering = ['organization', 'user']

    def __str__(self):
        return f'{self.user} - {self.organization} ({self.role})' 