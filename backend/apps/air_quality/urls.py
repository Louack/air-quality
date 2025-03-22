from rest_framework.routers import DefaultRouter

from apps.air_quality.views import LocationViewSet, AirPollutantReadingViewSet, PollutantViewSet, TagViewSet

router = DefaultRouter(trailing_slash=False)
router.register(prefix="pollutants", viewset=PollutantViewSet, basename="pollutants")
router.register(prefix="tags", viewset=TagViewSet, basename="tags")
router.register(prefix="locations", viewset=LocationViewSet, basename="locations")
router.register(prefix="readings", viewset=AirPollutantReadingViewSet, basename="readings")


urlpatterns = [

] + router.urls