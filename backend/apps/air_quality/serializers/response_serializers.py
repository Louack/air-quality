from apps.air_quality.serializers.query_serializers import (
    AirCompoundRadiusQuerySerializer,
)
from rest_framework import serializers


class RadiusStatsResponseSerializer(serializers.Serializer):
    """
    Serializer for statistics of air compound readings within a radius.
    """

    min_concentration = serializers.FloatField()
    max_concentration = serializers.FloatField()
    mean_concentration = serializers.FloatField()


class AirCompoundRadiusResponseSerializer(AirCompoundRadiusQuerySerializer):
    """
    Serializer for response of air compound readings within a radius.
    """

    stats = RadiusStatsResponseSerializer()
