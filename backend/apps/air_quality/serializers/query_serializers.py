from rest_framework import serializers

from apps.air_quality.models import Compound, AirCompoundReading


class AirCompoundRadiusQuerySerializer(serializers.Serializer):
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()
    compound = serializers.SlugRelatedField(
        queryset=Compound.objects.all(),
        slug_field="symbol",
    )
    concentration = serializers.CharField(
        choices=AirCompoundReading.CONCENTRATION_UNITS,
    )
