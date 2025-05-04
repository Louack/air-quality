from datetime import timedelta

import pytest
from apps.air_quality.models import AirCompoundReading
from apps.air_quality.tests.factories import (
    AirCompoundReadingFactory,
    CompoundFactory,
    LocationFactory,
    TagFactory,
)
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory
from core.tests.factories import APIClientFactory


@pytest.fixture
def api_client():
    user_to_log = UserFactory()
    return APIClientFactory(user=user_to_log)


@pytest.fixture
def unauthenticated_client():
    """Returns an unauthenticated API client for testing unauthorized access."""
    return APIClient()


@pytest.fixture
def tag():
    return TagFactory()


@pytest.fixture
def location(tag):
    return LocationFactory(tags=[tag])


@pytest.fixture
def compound():
    return CompoundFactory(
        full_name="Carbon Monoxide", symbol="CO", is_gaseous=True, molecular_weight=28
    )


@pytest.fixture
def air_reading(location, compound):
    return AirCompoundReadingFactory(
        location=location,
        compound=compound,
        entered_concentration_unit="ppm",
        entered_concentration_value=10.0,
    )


@pytest.mark.django_db
class TestAuthenticationRequired:
    """Test suite for authentication requirements."""

    @pytest.mark.parametrize("endpoint", [
        "locations-list",
        "readings-list",
        "compounds-list",
        "tags-list",
    ])
    def test_unauthorized_access(self, unauthenticated_client, endpoint):
        """Test that unauthorized access returns 401 for all protected endpoints."""
        url = reverse(endpoint)
        response = unauthenticated_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "credentials" in str(response.data).lower()

    def test_unauthorized_create_reading(self, unauthenticated_client, location, compound):
        """Test that unauthorized users cannot create readings."""
        url = reverse("readings-list")
        data = {
            "compound": compound.full_name,
            "location": location.name,
            "entered_concentration_value": 42.0,
            "entered_concentration_unit": "ug_m3",
        }
        response = unauthenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthorized_location_readings(self, unauthenticated_client, location):
        """Test that unauthorized users cannot access location readings."""
        url = reverse("locations-get-readings", args=[location.id])
        response = unauthenticated_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLocationViewSet:
    """Test suite for LocationViewSet."""

    def test_list_locations(self, api_client, location, tag):
        """Test retrieving a list of locations."""
        url = reverse("locations-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": location.pk,
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
                        "properties": {"name": location.name, "tags": [tag.name]},
                    }
                ],
            },
        }

    def test_retrieve_location(self, api_client, location, tag):
        """Test retrieving a single location."""
        url = reverse("locations-detail", args=[location.id])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["properties"]["name"] == location.name
        assert response.json() == {
            "id": location.pk,
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
            "properties": {"name": location.name, "tags": [tag.name]},
        }

    def test_create_location(self, api_client, tag):
        """Test creating a new location."""
        url = reverse("locations-list")
        data = {
            "name": "Test Location",
            "coordinates": {"type": "Point", "coordinates": [0, 0]},
            "tags": [
                tag.name,
            ],
        }

        response = api_client.post(url, data, format="json")
        json = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert isinstance(json["id"], int)
        assert json["type"] == "Feature"
        assert json["geometry"] == {"type": "Point", "coordinates": [0.0, 0.0]}
        assert json["properties"] == {"name": "Test Location", "tags": [tag.name]}

    def test_get_readings(self, api_client, location, air_reading, compound):
        """Test retrieving readings for a location."""
        url = reverse("locations-get-readings", args=[location.id])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": air_reading.pk,
                    "location": location.name,
                    "compound": compound.full_name,
                    "concentration_unit": air_reading.entered_concentration_unit,
                    "concentration_value": air_reading.entered_concentration_value,
                    "timestamp": air_reading.timestamp.isoformat().replace(
                        "+00:00", "Z"
                    ),
                }
            ],
        }


@pytest.mark.django_db
class TestAirCompoundReadingViewSet:
    """Test suite for AirCompoundReadingViewSet."""

    def test_list_readings(self, api_client, air_reading, location, compound):
        """Test retrieving a list of air compound readings."""
        url = reverse("readings-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": air_reading.pk,
                    "location": location.name,
                    "compound": compound.full_name,
                    "concentration_unit": air_reading.entered_concentration_unit,
                    "concentration_value": air_reading.entered_concentration_value,
                    "timestamp": air_reading.timestamp.isoformat().replace(
                        "+00:00", "Z"
                    ),
                }
            ],
        }

    def test_create_reading(self, api_client, location, compound):
        """Test creating a new air compound reading."""
        url = reverse("readings-list")
        data = {
            "compound": compound.full_name,
            "location": location.name,
            "entered_concentration_value": 42.0,
            "entered_concentration_unit": "ug_m3",
        }
        response = api_client.post(url, data, format="json")
        air_reading = AirCompoundReading.objects.last()

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "id": air_reading.pk,
            "location": location.name,
            "compound": compound.full_name,
            "entered_concentration_unit": air_reading.entered_concentration_unit,
            "entered_concentration_value": air_reading.entered_concentration_value,
            "timestamp": air_reading.timestamp.isoformat().replace("+00:00", "Z"),
        }

    def test_create_reading_with_invalid_unit(self, api_client, location, compound):
        """Test creating a reading with an invalid concentration unit."""
        url = reverse("readings-list")
        data = {
            "compound": compound.full_name,
            "location": location.name,
            "entered_concentration_value": 42.0,
            "entered_concentration_unit": "invalid_unit",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "entered_concentration_unit": ['"invalid_unit" is not a valid choice.']
        }

    def test_list_readings_with_concentration_unit(self, api_client, air_reading):
        """Test retrieving readings with a specific concentration unit."""
        url = reverse("readings-list")

        response = api_client.get(url, {"concentration_unit": "ppb"})
        reading = response.json()["results"][0]

        assert response.status_code == status.HTTP_200_OK
        assert reading["concentration_unit"] == "ppb"
        assert (
            reading["concentration_value"]
            == air_reading.entered_concentration_value * 1000
        )

    def test_list_readings_with_pagination(self, api_client, location, compound):
        """Test pagination of air compound readings."""
        # Create 15 readings
        readings = [
            AirCompoundReadingFactory(
                location=location,
                compound=compound,
            )
            for i in range(15)
        ]

        url = reverse("readings-list")
        # Test first page
        response = api_client.get(url + "?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 15
        assert len(response.data["results"]) == 10
        assert response.data["next"] is not None
        assert response.data["previous"] is None

        # Test second page
        response = api_client.get(url + "?page=2&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5
        assert response.data["next"] is None
        assert response.data["previous"] is not None

    @pytest.mark.parametrize("concentration_unit,concentration_value,expected_status", [
        ("invalid_unit", 42.0, status.HTTP_400_BAD_REQUEST),
        ("ppm", "not_a_number", status.HTTP_400_BAD_REQUEST),
        ("ug_m3", 0.0, status.HTTP_201_CREATED),
        ("ppb", - 10, status.HTTP_400_BAD_REQUEST),
    ])
    def test_create_reading_edge_cases(
        self, api_client, location, compound,
        concentration_unit, concentration_value, expected_status
    ):
        """Test creating readings with various edge cases."""
        url = reverse("readings-list")
        data = {
            "compound": compound.full_name,
            "location": location.name,
            "entered_concentration_value": concentration_value,
            "entered_concentration_unit": concentration_unit
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestTagViewSet:
    """Test suite for TagViewSet."""

    def test_list_tags(self, api_client, tag):
        """Test retrieving a list of tags."""
        url = reverse("tags-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"name": tag.name}],
        }

    def test_create_tag(self, api_client):
        """Test creating a new tag."""
        url = reverse("tags-list")
        data = {"name": "New Tag"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"name": "New Tag"}


@pytest.mark.django_db
class TestCompoundViewSet:
    """Test suite for CompoundViewSet."""

    def test_list_compounds(self, api_client, compound):
        """Test retrieving a list of compounds."""
        url = reverse("compounds-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {"symbol": "CO", "full_name": "Carbon Monoxide", "is_gaseous": True}
            ],
        }

    def test_create_compound(self, api_client):
        """Test creating a new compound."""
        url = reverse("compounds-list")
        data = {"symbol": "CO2", "full_name": "Carbon Dioxide", "is_gaseous": True}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "symbol": "CO2",
            "full_name": "Carbon Dioxide",
            "is_gaseous": True,
        }


@pytest.mark.django_db
class TestAirCompoundStatsWithinRadiusView:
    """Test suite for AirCompoundStatsWithinRadiusView."""

    @freeze_time("2025-01-27 0:00:00")
    def test_get_stats_within_radius(self, api_client, compound, location):
        """Test retrieving statistics for readings within a radius."""
        frozen_time = timezone.now()

        AirCompoundReadingFactory(
            location=location,
            compound=compound,
            entered_concentration_value=10.0,
            entered_concentration_unit="ug_m3",
        )
        AirCompoundReadingFactory(
            location=location,
            compound=compound,
            entered_concentration_value=20.0,
            entered_concentration_unit="ug_m3",
        )

        url = reverse("stats-radius-readings")
        params = {
            "latitude": 0,
            "longitude": 0,
            "radius": 10,
            "compound": compound.symbol,
            "start_date": (frozen_time - timedelta(days=1)).isoformat(),
            "end_date": (frozen_time + timedelta(days=1)).isoformat(),
            "concentration_unit": "ppb",
        }

        response = api_client.get(url, params)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "longitude": 0.0,
            "latitude": 0.0,
            "radius": 10.0,
            "compound": "CO",
            "concentration_unit": "ppb",
            "start_date": "2025-01-26T00:00:00Z",
            "end_date": "2025-01-28T00:00:00Z",
            "stats": {
                "min_concentration": 11.4519,
                "max_concentration": 22.9039,
                "mean_concentration": 17.1779,
            },
        }
