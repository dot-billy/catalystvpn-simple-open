import os
import yaml
from jinja2 import Template
from django.conf import settings


def load_template(template_name):
    """Load a configuration template from the samples directory."""
    template_path = os.path.join(settings.BASE_DIR, 'samples', template_name)
    with open(template_path, 'r') as f:
        return Template(f.read())


def _generate_firewall_rules(node):
    """Generate firewall rules from node's security groups."""
    inbound_rules = []
    outbound_rules = []

    for security_group in node.security_groups.all():
        for rule in security_group.firewall_rules.all():
            rule_data = {
                'port': rule.port,
                'proto': rule.protocol
            }

            # Add target specification
            if rule.host:
                rule_data['host'] = rule.host
            elif rule.cidr:
                rule_data['cidr'] = rule.cidr
            elif rule.group:
                rule_data['group'] = rule.group.name
            elif rule.groups.exists():
                rule_data['groups'] = [g.name for g in rule.groups.all()]

            # Add optional fields
            if rule.local_cidr:
                rule_data['local_cidr'] = rule.local_cidr
            if rule.ca_name:
                rule_data['ca_name'] = rule.ca_name
            if rule.ca_sha:
                rule_data['ca_sha'] = rule.ca_sha

            if rule.rule_type == 'inbound':
                inbound_rules.append(rule_data)
            else:
                outbound_rules.append(rule_data)

    return inbound_rules, outbound_rules


def generate_node_config(node, lighthouses):
    """Generate Nebula configuration for a node."""
    inbound_rules, outbound_rules = _generate_firewall_rules(node)
    
    config = {
        'pki': {
            'ca': node.organization.certificate_authority.ca_cert,
            'cert': node.certificate.cert,
            'key': node.certificate.key
        },
        'tun': {
            'mtu': 1300,
            'disabled': False,
            'tx_queue': 500,
            'drop_multicast': False,
            'drop_local_broadcast': False
        },
        'relay': {
            'am_relay': False,
            'use_relays': True
        },
        'cipher': 'aes',
        'listen': {
            'host': '0.0.0.0',
            'port': 4242
        },
        'punchy': {
            'punch': True
        },
        'logging': {
            'level': 'info',
            'format': 'text'
        },
        'firewall': {
            'inbound': inbound_rules,
            'outbound': outbound_rules,
            'conntrack': {
                'tcp_timeout': '12m',
                'udp_timeout': '3m',
                'default_timeout': '10m'
            },
            'inbound_action': 'drop',
            'outbound_action': 'drop'
        },
        'lighthouse': {
            'hosts': [
                {
                    'hostname': lighthouse.hostname,
                    'public_ip': lighthouse.public_ip,
                    'port': lighthouse.port
                }
                for lighthouse in lighthouses
            ],
            'interval': 60,
            'am_lighthouse': False
        },
        'static_host_map': None
    }

    return config


def generate_lighthouse_config(lighthouse):
    """Generate Nebula configuration for a lighthouse."""
    inbound_rules, outbound_rules = _generate_firewall_rules(lighthouse)
    
    config = {
        'pki': {
            'ca': lighthouse.organization.certificate_authority.ca_cert,
            'cert': lighthouse.certificate.cert,
            'key': lighthouse.certificate.key
        },
        'tun': {
            'mtu': 1300,
            'disabled': False,
            'tx_queue': 500,
            'drop_multicast': False,
            'drop_local_broadcast': False
        },
        'relay': {
            'am_relay': False,
            'use_relays': True
        },
        'cipher': 'aes',
        'listen': {
            'host': '0.0.0.0',
            'port': lighthouse.port
        },
        'punchy': {
            'punch': True
        },
        'logging': {
            'level': 'info',
            'format': 'text'
        },
        'firewall': {
            'inbound': inbound_rules,
            'outbound': outbound_rules,
            'conntrack': {
                'tcp_timeout': '12m',
                'udp_timeout': '3m',
                'default_timeout': '10m'
            },
            'inbound_action': 'drop',
            'outbound_action': 'drop'
        },
        'lighthouse': {
            'hosts': [],
            'interval': 60,
            'am_lighthouse': True
        },
        'static_host_map': None
    }

    return config 