from apps.air_quality.models import AirCompoundReading, Compound, Location, Tag
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    """

    class Meta:
        model = Tag
        fields = ("name",)


class CompoundSerializer(serializers.ModelSerializer):
    """
    Serializer for Compound model.
    """

    class Meta:
        model = Compound
        fields = ("symbol", "full_name", "is_gaseous")


class LocationSerializer(GeoFeatureModelSerializer):
    """
    Serializer for Location model with geographical data.
    """

    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(), slug_field="name", many=True, required=False
    )

    class Meta:
        model = Location
        geo_field = "coordinates"
        fields = ("id", "name", "coordinates", "tags")

    @staticmethod
    def validate_coordinates(value):
        """
        Validates geographical coordinates.
        """
        error_messages = []
        longitude, latitude = value.coords
        if not (-180 <= longitude <= 180):
            error_messages.append("Longitude must be between -180 and 180.")
        if not (-90 <= latitude <= 90):
            error_messages.append("Latitude must be between -90 and 90.")

        if error_messages:
            raise ValidationError(error_messages)

        return value


class AirCompoundReadingSerializer(serializers.ModelSerializer):
    """
    Serializer for AirCompoundReading model.
    """

    location = serializers.SlugRelatedField(
        slug_field="name", queryset=Location.objects.all()
    )
    compound = serializers.SlugRelatedField(
        slug_field="full_name",
        queryset=Compound.objects.all(),
    )
    concentration_unit = serializers.SerializerMethodField(default=None)
    concentration_value = serializers.SerializerMethodField(default=None)

    class Meta:
        model = AirCompoundReading
        fields = (
            "id",
            "location",
            "compound",
            "concentration_unit",
            "concentration_value",
            "timestamp",
        )

    def get_concentration_unit(self, obj):
        """
        Returns the concentration unit from context or the entered unit.
        """
        if hasattr(obj, "concentration_value") and obj.concentration_value is not None:
            return self.context.get("concentration_unit")
        return obj.entered_concentration_unit

    def get_concentration_value(self, obj):
        """
        Returns a converted concentration value or the entered concentration value.
        """
        if hasattr(obj, "concentration_value") and obj.concentration_value is not None:
            return round(obj.concentration_value, 4)
        return round(obj.entered_concentration_value, 4)


class CreateAirCompoundReadingSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating AirCompoundReading instances.
    """

    location = serializers.SlugRelatedField(
        slug_field="name", queryset=Location.objects.all()
    )
    compound = serializers.SlugRelatedField(
        slug_field="full_name",
        queryset=Compound.objects.all(),
    )

    class Meta:
        model = AirCompoundReading
        fields = (
            "id",
            "location",
            "compound",
            "entered_concentration_value",
            "entered_concentration_unit",
            "timestamp",
        )

    def validate(self, attrs):
        """
        Validates compound and concentration unit compatibility.
        """
        error_messages = []
        compound = attrs.get("compound")
        unit = attrs.get("entered_concentration_unit")
        if not compound.is_gaseous and unit in ("ppm", "ppb"):
            error_messages.append(
                "Non-gaseous compound cannot be expressed in ppm or ppb."
            )

        if error_messages:
            return ValidationError(error_messages)
        return attrs
