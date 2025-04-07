import pytest
from django.urls import reverse
from rest_framework import status
from api.models import SecurityGroup, Node, Lighthouse, FirewallRule, Network
from tests.external.conftest import create_test_organization, create_test_user, create_test_node, create_test_lighthouse


@pytest.fixture
def security_group_data():
    return {
        'name': 'test-security-group',
        'description': 'Test security group',
        'firewall_rules': [
            {
                'rule_type': 'inbound',
                'protocol': 'tcp',
                'port': 80,
                'cidr': '0.0.0.0/0'
            },
            {
                'rule_type': 'outbound',
                'protocol': 'tcp',
                'port': 443,
                'cidr': '0.0.0.0/0'
            }
        ]
    }


@pytest.fixture
def security_group(organization, security_group_data):
    return SecurityGroup.objects.create(
        organization=organization,
        name=security_group_data['name'],
        description=security_group_data['description']
    )


def test_create_security_group(api_client, organization, security_group_data):
    """Test creating a security group with firewall rules."""
    url = reverse('organization-security-groups-list', kwargs={'organization_id': organization.id})
    response = api_client.post(url, security_group_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == security_group_data['name']
    assert response.data['description'] == security_group_data['description']
    assert len(response.data['firewall_rules']) == 2


def test_create_security_group_with_members(api_client, organization, security_group_data, node, lighthouse):
    """Test creating a security group with members."""
    security_group_data['node_ids'] = [str(node.id)]
    security_group_data['lighthouse_ids'] = [str(lighthouse.id)]
    
    url = reverse('organization-security-groups-list', kwargs={'organization_id': organization.id})
    response = api_client.post(url, security_group_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    security_group = SecurityGroup.objects.get(id=response.data['id'])
    assert node in security_group.nodes.all()
    assert lighthouse in security_group.lighthouses.all()


def test_add_remove_nodes(api_client, organization, security_group, node):
    """Test adding and removing nodes from a security group."""
    # Add node
    url = reverse('organization-security-groups-add-nodes', kwargs={
        'organization_id': organization.id,
        'pk': security_group.id
    })
    response = api_client.post(url, {'node_ids': [str(node.id)]})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert node in security_group.nodes.all()

    # Remove node
    url = reverse('organization-security-groups-remove-nodes', kwargs={
        'organization_id': organization.id,
        'pk': security_group.id
    })
    response = api_client.delete(url, {'node_ids': [str(node.id)]})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert node not in security_group.nodes.all()


def test_add_remove_lighthouses(api_client, organization, security_group, lighthouse):
    """Test adding and removing lighthouses from a security group."""
    # Add lighthouse
    url = reverse('organization-security-groups-add-lighthouses', kwargs={
        'organization_id': organization.id,
        'pk': security_group.id
    })
    response = api_client.post(url, {'lighthouse_ids': [str(lighthouse.id)]})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert lighthouse in security_group.lighthouses.all()

    # Remove lighthouse
    url = reverse('organization-security-groups-remove-lighthouses', kwargs={
        'organization_id': organization.id,
        'pk': security_group.id
    })
    response = api_client.delete(url, {'lighthouse_ids': [str(lighthouse.id)]})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert lighthouse not in security_group.lighthouses.all()


def test_add_remove_firewall_rules(api_client, organization, security_group):
    """Test adding and removing firewall rules from a security group."""
    # Add rule
    url = reverse('organization-security-groups-add-rule', kwargs={
        'organization_id': organization.id,
        'pk': security_group.id
    })
    rule_data = {
        'rule_type': 'inbound',
        'protocol': 'tcp',
        'port': 80,
        'cidr': '0.0.0.0/0'
    }
    response = api_client.post(url, rule_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert security_group.firewall_rules.count() == 1

    # Remove rule
    url = reverse('organization-security-groups-remove-rule', kwargs={
        'organization_id': organization.id,
        'pk': security_group.id
    })
    response = api_client.delete(url, {'rule_id': str(response.data['id'])})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert security_group.firewall_rules.count() == 0


def test_security_group_validation(api_client, organization):
    """Test security group validation rules."""
    url = reverse('organization-security-groups-list', kwargs={'organization_id': organization.id})
    
    # Test invalid CIDR
    data = {
        'name': 'invalid-cidr',
        'firewall_rules': [{
            'rule_type': 'inbound',
            'protocol': 'tcp',
            'port': 80,
            'cidr': 'invalid-cidr'
        }]
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Invalid CIDR notation' in str(response.data)

    # Test missing port for non-ICMP protocol
    data = {
        'name': 'missing-port',
        'firewall_rules': [{
            'rule_type': 'inbound',
            'protocol': 'tcp',
            'cidr': '0.0.0.0/0'
        }]
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Port is required for non-ICMP protocols' in str(response.data)

    # Test port specified for ICMP
    data = {
        'name': 'icmp-with-port',
        'firewall_rules': [{
            'rule_type': 'inbound',
            'protocol': 'icmp',
            'port': 80,
            'cidr': '0.0.0.0/0'
        }]
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Port should not be specified for ICMP protocol' in str(response.data)


def test_security_group_cross_organization(api_client, organization, other_organization):
    """Test security group cross-organization restrictions."""
    # Create a security group in another organization
    other_security_group = SecurityGroup.objects.create(
        organization=other_organization,
        name='other-security-group'
    )
    
    # Try to add a rule referencing the other organization's security group
    url = reverse('organization-security-groups-add-rule', kwargs={
        'organization_id': organization.id,
        'pk': security_group.id
    })
    rule_data = {
        'rule_type': 'inbound',
        'protocol': 'tcp',
        'port': 80,
        'group': str(other_security_group.id)
    }
    response = api_client.post(url, rule_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Referenced security group must belong to the same organization' in str(response.data)


def test_node_with_security_groups(api_client, organization, security_group):
    """Test creating a node with security groups."""
    url = reverse('organization-nodes-list', kwargs={'organization_id': organization.id})
    data = {
        'name': 'test-node',
        'hostname': 'test-node.example.com',
        'security_group_ids': [str(security_group.id)]
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.data['security_groups']) == 1
    assert response.data['security_groups'][0]['id'] == str(security_group.id)


def test_lighthouse_with_security_groups(api_client, organization, security_group):
    """Test creating a lighthouse with security groups."""
    url = reverse('organization-lighthouses-list', kwargs={'organization_id': organization.id})
    data = {
        'name': 'test-lighthouse',
        'hostname': 'test-lighthouse.example.com',
        'public_ip': '1.2.3.4',
        'port': 4242,
        'security_group_ids': [str(security_group.id)]
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.data['security_groups']) == 1
    assert response.data['security_groups'][0]['id'] == str(security_group.id) 