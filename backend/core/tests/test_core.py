import pytest
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_api_documentation_endpoints():
    """Test that API documentation endpoints are accessible."""
    response = APIClient().get("/doc")
    assert response.status_code == status.HTTP_200_OK