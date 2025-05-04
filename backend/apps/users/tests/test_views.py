import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestRegistrationView:
    """Test suite for user registration functionality."""

    def test_successful_registration(self, api_client):
        """Test successful user registration with valid data."""
        url = reverse("register")
        data = {
            "username": "test_user",
            "password": "StrongPass123!",
            "password2": "StrongPass123!"
        }

        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="test_user").exists()
        user = User.objects.get(username="test_user")
        assert user.check_password("StrongPass123!")

    def test_registration_with_existing_username(self, api_client):
        """Test registration with an already existing username."""
        existing_user = UserFactory(username="existing_user")
        
        url = reverse("register")
        data = {
            "username": "existing_user",
            "password": "StrongPass123!",
            "password2": "StrongPass123!"
        }

        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_mismatched_passwords(self, api_client):
        """Test registration with non-matching passwords."""
        url = reverse("register")
        data = {
            "username": "test_user",
            "password": "StrongPass123!",
            "password2": "DifferentPass123!"
        }

        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_weak_password(self, api_client):
        """Test registration with a weak password."""
        url = reverse("register")
        data = {
            "username": "test_user",
            "password": "weak",
            "password2": "weak"
        }

        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_missing_fields(self, api_client):
        """Test registration with missing required fields."""
        url = reverse("register")
        data = {
            "username": "test_user"
        }

        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("username", [
        "",  # empty
        "a" * 151,  # too long
    ])
    def test_registration_with_invalid_usernames(self, api_client, username):
        """Test registration with various invalid username formats."""
        url = reverse("register")
        data = {
            "username": username,
            "password": "StrongPass123!",
            "password2": "StrongPass123!"
        }

        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST 