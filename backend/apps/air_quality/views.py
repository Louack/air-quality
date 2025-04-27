from apps.air_quality.conversions import get_qs_with_converted_concentration
from apps.air_quality.filters import AirCompoundReadingFilterSet, LocationFilterSet
from apps.air_quality.models import AirCompoundReading, Compound, Location, Tag
from apps.air_quality.serializers.model_serializers import (
    AirCompoundReadingSerializer,
    CompoundSerializer,
    CreateAirCompoundReadingSerializer,
    LocationSerializer,
    TagSerializer,
)
from apps.air_quality.serializers.query_serializers import (
    AirCompoundRadiusQuerySerializer,
)
from apps.air_quality.serializers.response_serializers import (
    AirCompoundRadiusResponseSerializer,
)
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Avg, Max, Min
from django.db.models.functions import Round
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView


class LocationViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for Location resources.
    """

    queryset = Location.objects.prefetch_related("tags").order_by("name")
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LocationFilterSet
    ordering_fields = ["id", "name"]

    @swagger_auto_schema(responses={200: AirCompoundReadingSerializer})
    @action(detail=True, methods=["get"], url_path="readings")
    def get_readings(self, request, pk=None):
        """
        Retrieves air compound readings for a specific location.
        """
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
    """
    ViewSet for AirCompoundReading resources.
    """

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AirCompoundReadingFilterSet
    ordering_fields = ["timestamp", "location"]

    def get_queryset(self):
        """
        Returns a queryset of AirCompoundReading objects with related data.
        """
        qs = AirCompoundReading.objects.select_related("compound", "location").order_by(
            "-timestamp"
        )
        return qs

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action.
        """
        if self.action in ["create", "update", "partial_update"]:
            return CreateAirCompoundReadingSerializer
        return AirCompoundReadingSerializer

    def get_serializer_context(self):
        """
        Adds concentration_unit from query parameters to the serializer context.
        """
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
    """
    ViewSet for Tag resources.
    """

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
    """
    ViewSet for Compound resources.
    """

    serializer_class = CompoundSerializer
    queryset = Compound.objects.all()
    filter_backends = [
        OrderingFilter,
    ]
    ordering_fields = ["full_name", "symbol"]


class AirCompoundStatsWithinRadiusView(APIView):
    """
    API view to retrieve statistics for air compound readings within a specified radius.
    """

    @swagger_auto_schema(
        query_serializer=AirCompoundRadiusQuerySerializer,
        responses={200: AirCompoundRadiusResponseSerializer},
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieves statistics for air compound readings within a radius.
        """
        query_serializer = AirCompoundRadiusQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        response_data = {
            **query_serializer.validated_data,
            "stats": self.get_radius_stats(data=query_serializer.validated_data),
        }

        serializer = AirCompoundRadiusResponseSerializer(instance=response_data)

        return Response(data=serializer.data, status=200)

    def get_radius_stats(self, data):
        """
        Calculates statistics for air compound readings within the specified radius.
        """
        qs = self.get_queryset_within_radius(data)
        return qs.aggregate(
            min_concentration=Round(Min("concentration_value"), 4),
            max_concentration=Round(Max("concentration_value"), 4),
            mean_concentration=Round(Avg("concentration_value"), 4),
        )

    @staticmethod
    def get_queryset_within_radius(data):
        """
        Returns a queryset of air compound readings within the specified radius.
        """
        center = Point(
            x=data.get("longitude"),
            y=data.get("latitude"),
            srid=4326,
        )
        qs = AirCompoundReading.objects.filter(
            compound=data.get("compound"),
            location__coordinates__dwithin=(center, D(km=data.get("radius"))),
            timestamp__gte=data.get("start_date"),
            timestamp__lte=data.get("end_date"),
        )
        return get_qs_with_converted_concentration(
            queryset=qs, target_unit=data.get("concentration_unit")
        )
