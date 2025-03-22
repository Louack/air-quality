from datetime import datetime, timedelta

from django.db.models import Avg
from django.db.models.functions import Round
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from apps.air_quality.models import Location, Tag, Pollutant, AirPollutantReading


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name",)


class PollutantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pollutant
        fields = ("symbol", "full_name",)


class LocationSerializer(GeoFeatureModelSerializer):
    tags_to_link = serializers.ListField(
        child=serializers.CharField(max_length=64), write_only=True, required=False
    )
    tags = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Location
        geo_field = "coordinates"
        fields = ("id", "name", "coordinates", "tags", "tags_to_link")

    def get_tags(self, obj):
        return obj.tags.all().values_list("name", flat=True)

    def validate_coordinates(self, value):
        longitude, latitude = value.coords
        if not (-180 <= longitude <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        if not (-90 <= latitude <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def create(self, validated_data):
        tag_names = validated_data.pop("tags_to_link", [])
        location = Location.objects.create(**validated_data)
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        location.tags.set(tags)
        return location

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tags_to_link", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        instance.tags.set(tags)

        return instance


class AirPollutantReadingSerializer(serializers.ModelSerializer):
    location_to_link = serializers.CharField(max_length=64, write_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    pollutant_to_link = serializers.CharField(max_length=64, write_only=True)
    pollutant = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AirPollutantReading
        fields = ("id", "location", "location_to_link", "pollutant","pollutant_to_link")

    def get_location(self, obj):
        return obj.location.name

    def validate(self, validated_data):
        errors = {}

        try:
            validated_data = super().validate(validated_data)
        except serializers.ValidationError as e:
            errors.update(e.detail)

        location_name = validated_data.get("location_to_link")
        pollutant_name = validated_data.get("pollutant_to_link")

        if location_name:
            try:
                validated_data["location"] = Location.objects.get(name=location_name)
            except Location.DoesNotExist:
                errors["location_to_link"] = "Location with this name does not exist"

        if pollutant_name:
            try:
                validated_data["pollutant"] = Pollutant.objects.get(name=pollutant_name)
            except Pollutant.DoesNotExist:
                errors["pollutant_to_link"] = "Pollutant with this name does not exist"

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    # @staticmethod
    # def get_location_obj(location_name: str) -> Location:
    #     try:
    #         location = Location.objects.get(name=location_name)
    #         return location
    #     except Location.DoesNotExist:
    #         raise serializers.ValidationError(
    #             "Location with this name does not exist"
    #         )
    #
    #
    # @staticmethod
    # def get_pollutant_obj(pollutant_name: str) -> Pollutant:
    #     try:
    #         pollutant = Pollutant.objects.get(name=pollutant_name)
    #         return pollutant
    #     except Pollutant.DoesNotExist:
    #         raise serializers.ValidationError(
    #             "Pollutant with this name does not exist"
    #         )
    #
    # def create(self, validated_data):
    #     location_name = validated_data.pop("location_to_link")
    #     pollutant_name = validated_data.pop("pollutant_to_link")
    #
    #     validated_data["location"] = self.get_location_obj(location_name=location_name)
    #     validated_data["pollutant"] = self.get_pollutant_obj(pollutant_name=pollutant_name)
    #
    #     reading = AirPollutantReading.objects.create(**validated_data)
    #
    #     return reading
    #
    # def update(self, instance, validated_data):
    #     location_name = validated_data.pop("location_to_link", None)
    #     pollutant_name = validated_data.pop("pollutant_to_link")
    #
    #     if location_name:
    #         instance.location = self.get_location_obj(location_name=location_name)
    #
    #     if pollutant_name:
    #         instance.pollutant = self.get_pollutant_obj(pollutant_name=pollutant_name)
    #
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #
    #     instance.save()
    #
    #     return instance
