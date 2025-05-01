import pytest
from django.conf import settings


def pytest_configure():
    """Configure pytest for Django."""
    settings.DEBUG = False
