"""
Basic tests for the API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


def test_user_registration(api_client):
    """Test user registration endpoint."""
    url = reverse('user-list')
    data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass123'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username='newuser').exists()


def test_user_login(api_client, user):
    """Test user login endpoint."""
    url = reverse('token_obtain_pair')
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_protected_endpoint(api_client, user):
    """Test access to protected endpoint."""
    # First, get the token
    url = reverse('token_obtain_pair')
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    response = api_client.post(url, data, format='json')
    token = response.data['access']

    # Then try to access a protected endpoint
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('user-me')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'testuser' 