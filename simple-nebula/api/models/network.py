import uuid
import ipaddress
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address
from ipaddress import IPv4Network, IPv4Address

from .organization import Organization
from .certificates import Certificate


def validate_cidr(value):
    try:
        network = ipaddress.ip_network(value)
        if network.version != 4:
            raise ValidationError('Only IPv4 networks are supported')
    except ValueError as e:
        raise ValidationError(f'Invalid CIDR notation: {str(e)}')


class Network(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='networks'
    )
    name = models.CharField(_('name'), max_length=255)
    cidr = models.CharField(_('CIDR'), max_length=18, validators=[validate_cidr])
    description = models.TextField(_('description'), blank=True)
    is_primary = models.BooleanField(_('is primary'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('network')
        verbose_name_plural = _('networks')
        unique_together = ('organization', 'name')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.cidr})'

    def clean(self):
        try:
            network = ipaddress.ip_network(self.cidr)
            if network.version != 4:
                raise ValidationError('Only IPv4 networks are supported')
        except ValueError as e:
            raise ValidationError(f'Invalid CIDR notation: {str(e)}')

        if self.is_primary:
            # Ensure only one primary network per organization
            if self.organization:  # Check if organization is set
                primary = Network.objects.filter(
                    organization=self.organization,
                    is_primary=True
                ).exclude(id=self.id)
                if primary.exists():
                    raise ValidationError('Organization already has a primary network')

    def get_available_ip(self):
        """Get the next available IP in this network."""
        network = ipaddress.ip_network(self.cidr)
        # Skip network address and broadcast address
        available_ips = set(str(ip) for ip in network.hosts())
        
        # Get all used IPs in this network
        used_ips = set()
        
        # Get all nodes' IPs that are within this network's CIDR range
        nodes_ips = Node.objects.filter(
            organization=self.organization,
            nebula_ip__isnull=False,
            network=self
        ).values_list('nebula_ip', flat=True)
        used_ips.update(nodes_ips)
        
        # Get all lighthouses' IPs that are within this network's CIDR range
        lighthouses_ips = Lighthouse.objects.filter(
            organization=self.organization,
            nebula_ip__isnull=False,
            network=self
        ).values_list('nebula_ip', flat=True)
        used_ips.update(lighthouses_ips)
        
        available_ips = available_ips - used_ips
        if not available_ips:
            raise ValidationError('No available IPs in this network')
        return sorted(available_ips)[0]

    def is_ip_available(self, ip):
        """Check if an IP is available in this network."""
        network = ipaddress.ip_network(self.cidr)
        if ipaddress.ip_address(ip) not in network:
            return False
        
        # Check if the IP is already used by a node or lighthouse in this network
        return not (
            Node.objects.filter(
                organization=self.organization,
                nebula_ip=ip,
                network=self
            ).exists() or
            Lighthouse.objects.filter(
                organization=self.organization,
                nebula_ip=ip,
                network=self
            ).exists()
        )


class SecurityGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='security_groups'
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('security group')
        verbose_name_plural = _('security groups')
        unique_together = ('organization', 'name')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.organization})'


class FirewallRule(models.Model):
    RULE_TYPES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    PROTOCOLS = [
        ('tcp', 'TCP'),
        ('udp', 'UDP'),
        ('icmp', 'ICMP'),
        ('any', 'Any'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    security_group = models.ForeignKey('SecurityGroup', on_delete=models.CASCADE, related_name='firewall_rules')
    rule_type = models.CharField(max_length=10, choices=RULE_TYPES)
    protocol = models.CharField(max_length=4, choices=PROTOCOLS)
    port = models.CharField(max_length=20, null=True, blank=True)
    host = models.CharField(max_length=255, null=True, blank=True)
    cidr = models.CharField(max_length=18, null=True, blank=True)
    local_cidr = models.CharField(max_length=18, null=True, blank=True)
    group = models.ForeignKey('SecurityGroup', on_delete=models.CASCADE, null=True, blank=True, related_name='referenced_by_rules')
    groups = models.ManyToManyField('SecurityGroup', blank=True, related_name='referenced_by_rules_many')
    ca_name = models.CharField(max_length=255, null=True, blank=True)
    ca_sha = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        verbose_name = _('firewall rule')
        verbose_name_plural = _('firewall rules')

    def clean(self):
        if not any([self.host, self.cidr, self.group, self.groups.exists()]):
            raise ValidationError(_('At least one of host, cidr, group, or groups must be specified'))

        specified_fields = sum([bool(self.host), bool(self.cidr), bool(self.group), self.groups.exists()])
        if specified_fields > 1:
            raise ValidationError(_('Only one of host, cidr, group, or groups can be specified'))

        if self.cidr:
            try:
                IPv4Network(self.cidr)
            except ValueError:
                raise ValidationError(_('Invalid CIDR notation'))

        if self.local_cidr:
            try:
                IPv4Network(self.local_cidr)
            except ValueError:
                raise ValidationError(_('Invalid local CIDR notation'))

        if self.port and self.port != 'any':
            if '-' in self.port:
                try:
                    start, end = map(int, self.port.split('-'))
                    if not (1 <= start <= 65535 and 1 <= end <= 65535 and start <= end):
                        raise ValueError
                except ValueError:
                    raise ValidationError(_('Invalid port range format. Use "start-end" where 1 <= start <= end <= 65535'))
            else:
                try:
                    port = int(self.port)
                    if not (1 <= port <= 65535):
                        raise ValueError
                except ValueError:
                    raise ValidationError(_('Port must be between 1 and 65535'))

        if self.protocol == 'icmp' and self.port is not None:
            raise ValidationError(_('Port should not be specified for ICMP protocol'))

        if self.protocol != 'icmp' and self.port is None:
            raise ValidationError(_('Port is required for non-ICMP protocols'))

    def __str__(self):
        if self.host:
            target = f'host:{self.host}'
        elif self.cidr:
            target = self.cidr
        elif self.group:
            target = f'sg:{self.group.name}'
        elif self.groups.exists():
            target = f'sgs:{",".join(g.name for g in self.groups.all())}'
        else:
            target = 'any'
            
        return f'{self.rule_type} {self.protocol} {self.port or "*"} {target}'


class BaseNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE
    )
    name = models.CharField(_('name'), max_length=255)
    hostname = models.CharField(_('hostname'), max_length=255)
    nebula_ip = models.GenericIPAddressField(_('Nebula IP'), protocol='IPv4', null=True, blank=True)
    network = models.ForeignKey(
        Network,
        on_delete=models.PROTECT,
        related_name='%(class)ss',
        null=True,
        blank=True
    )
    certificate = models.OneToOneField(
        'Certificate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s'
    )
    security_groups = models.ManyToManyField(
        SecurityGroup,
        related_name='%(class)ss'
    )
    last_check_in = models.DateTimeField(_('last check-in'), null=True, blank=True)
    config = models.JSONField(_('config'), default=dict)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        abstract = True

    def clean(self):
        if self.nebula_ip and self.network:
            if not self.network.is_ip_available(self.nebula_ip):
                raise ValidationError('IP address is not available in this network')
            network = ipaddress.ip_network(self.network.cidr)
            if ipaddress.ip_address(self.nebula_ip) not in network:
                raise ValidationError('IP address is not in network CIDR range')

    def save(self, *args, **kwargs):
        if not self.network:
            # Get the primary network for the organization
            self.network = Network.objects.get(organization=self.organization, is_primary=True)
        
        if not self.nebula_ip:
            # Get the next available IP from the network
            self.nebula_ip = self.network.get_available_ip()
            
        super().save(*args, **kwargs)


class Node(BaseNode):
    lighthouse = models.ForeignKey(
        'Lighthouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nodes'
    )

    class Meta:
        verbose_name = _('node')
        verbose_name_plural = _('nodes')
        unique_together = ('organization', 'name')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.nebula_ip})'


class Lighthouse(BaseNode):
    public_ip = models.GenericIPAddressField(_('public IP'), protocol='both')
    port = models.IntegerField(_('port'), default=4242)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('lighthouse')
        verbose_name_plural = _('lighthouses')
        unique_together = (('organization', 'name'),)
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.public_ip}:{self.port})' 