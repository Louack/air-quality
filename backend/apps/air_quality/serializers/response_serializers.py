from rest_framework import serializers

from apps.air_quality.serializers.query_serializers import (
    AirCompoundRadiusQuerySerializer,
)


class RadiusStatsResponseSerializer(serializers.Serializer):
    min_concentration = serializers.FloatField()
    max_concentration = serializers.FloatField()
    mean_concentration = serializers.FloatField()


class AirCompoundRadiusResponseSerializer(AirCompoundRadiusQuerySerializer):
    stats = RadiusStatsResponseSerializer()
