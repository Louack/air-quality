from rest_framework import serializers

from apps.air_quality.models import Compound, AirCompoundReading


class AirCompoundRadiusQuerySerializer(serializers.Serializer):
    longitude = serializers.FloatField(
        min_value=-180, max_value=180, help_text="Longitude of the center point"
    )
    latitude = serializers.FloatField(
        min_value=-90, max_value=90, help_text="Latitude of the center point"
    )
    radius = serializers.FloatField(
        min_value=0, max_value=100, help_text="radius in km"
    )
    compound = serializers.SlugRelatedField(
        queryset=Compound.objects.all(),
        slug_field="symbol",
    )
    concentration_unit = serializers.ChoiceField(
        choices=AirCompoundReading.CONCENTRATION_UNITS,
    )
