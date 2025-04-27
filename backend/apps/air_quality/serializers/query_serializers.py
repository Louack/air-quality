from apps.air_quality.models import AirCompoundReading, Compound
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class AirCompoundRadiusQuerySerializer(serializers.Serializer):
    """
    Serializer for query parameters for air compound readings within a radius.
    """

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
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    def validate(self, attrs):
        """
        Validates that start_date is not greater than end_date.
        """
        error_messages = []
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date > end_date:
            error_messages.append("'start_date' cannot be greater than 'end_date'.")

        if error_messages:
            raise ValidationError(error_messages)

        return attrs
