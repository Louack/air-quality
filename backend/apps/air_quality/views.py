from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter

from apps.air_quality.filters import AirCompoundReadingFilterSet, LocationFilterSet
from apps.air_quality.models import AirCompoundReading, Compound, Location, Tag
from apps.air_quality.serializers.model_serializers import (
    AirCompoundReadingSerializer,
    CompoundSerializer,
    CreateAirCompoundReadingSerializer,
    LocationSerializer,
    TagSerializer,
)


class LocationViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Location.objects.prefetch_related("tags").order_by("name")
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LocationFilterSet
    ordering_fields = ["id", "name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LocationSerializer
        return LocationSerializer

    @swagger_auto_schema(responses={200: AirCompoundReadingSerializer})
    @action(detail=True, methods=["get"], url_path="readings")
    def get_readings(self, request, pk=None):
        location = self.get_object()
        readings = location.air_readings.all()

        paginated_readings = self.paginate_queryset(readings)
        serializer = AirCompoundReadingSerializer(paginated_readings, many=True)

        return self.get_paginated_response(serializer.data)


class AirCompoundReadingViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AirCompoundReadingFilterSet
    ordering_fields = ["timestamp", "location"]

    def get_queryset(self):
        qs = AirCompoundReading.objects.select_related("compound", "location").order_by(
            "-timestamp"
        )
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CreateAirCompoundReadingSerializer
        return AirCompoundReadingSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["concentration_unit"] = self.request.query_params.get(
            "concentration_unit"
        )
        return context


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
    filter_backends = [
        OrderingFilter,
    ]
    ordering_fields = [
        "name",
    ]


class CompoundViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = CompoundSerializer
    queryset = Compound.objects.all()
    filter_backends = [
        OrderingFilter,
    ]
    ordering_fields = ["full_name", "symbol"]
