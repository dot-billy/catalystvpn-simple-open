# Generated by Django 5.2 on 2025-04-02 16:08

from django.db import migrations
import uuid


def create_primary_networks(apps, schema_editor):
    Organization = apps.get_model('api', 'Organization')
    Network = apps.get_model('api', 'Network')

    for org in Organization.objects.all():
        Network.objects.create(
            id=uuid.uuid4(),
            name='Primary Network',
            cidr='10.0.0.0/24',
            description='Primary network for organization',
            is_primary=True,
            organization=org
        )


def reverse_primary_networks(apps, schema_editor):
    Network = apps.get_model('api', 'Network')
    Network.objects.filter(is_primary=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_network'),
    ]

    operations = [
        migrations.RunPython(create_primary_networks, reverse_primary_networks),
    ] 