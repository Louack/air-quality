from apps.air_quality.views import (
    AirCompoundReadingViewSet,
    AirCompoundStatsWithinRadiusView,
    CompoundViewSet,
    LocationViewSet,
    TagViewSet,
)
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(prefix="compounds", viewset=CompoundViewSet, basename="compounds")
router.register(prefix="tags", viewset=TagViewSet, basename="tags")
router.register(prefix="locations", viewset=LocationViewSet, basename="locations")
router.register(
    prefix="readings", viewset=AirCompoundReadingViewSet, basename="readings"
)


urlpatterns = [
    path(
        "readings/stats/radius",
        AirCompoundStatsWithinRadiusView.as_view(),
        name="stats-radius-readings",
    )
] + router.urls
