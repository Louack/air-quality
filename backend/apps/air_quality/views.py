from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter

from apps.air_quality.models import Location, AirPollutantReading, Pollutant, Tag
from apps.air_quality.serializers.model_serializers import LocationSerializer, AirPollutantReadingSerializer, \
    PollutantSerializer, TagSerializer


class LocationViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Location.objects.all().order_by("name")
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["id", "name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LocationSerializer
        return LocationSerializer

    @swagger_auto_schema(responses={200: AirPollutantReadingSerializer})
    @action(detail=True, methods=["get"], url_path="readings")
    def get_readings(self, request, pk=None):
        location = self.get_object()
        readings = location.air_pollutant_readings.all()

        paginated_readings = self.paginate_queryset(readings)
        serializer = AirPollutantReadingSerializer(paginated_readings, many=True)

        return self.get_paginated_response(serializer.data)


class AirPollutantReadingViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = AirPollutantReadingSerializer
    queryset = AirPollutantReading.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["date", "location"]


class TagViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    filter_backends = [OrderingFilter,]
    ordering_fields = ["name",]


class PollutantViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = PollutantSerializer
    queryset = Pollutant.objects.all()
    filter_backends = [OrderingFilter,]
    ordering_fields = ["name",]



