from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django_filters.rest_framework import FilterSet, filters
from rest_framework.exceptions import ValidationError

from apps.air_quality.conversions import get_qs_with_converted_concentration
from apps.air_quality.models import AirCompoundReading, Compound, Location, Tag


class LocationFilterSet(FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    tag = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(), to_field_name="name", field_name="tags__name"
    )


class AirCompoundReadingFilterSet(FilterSet):
    tag = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name="name",
        field_name="location__tags__name",
    )
    compound = filters.ModelMultipleChoiceFilter(
        queryset=Compound.objects.all(),
        to_field_name="symbol",
        field_name="compound__symbol",
    )
    location = filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.all(),
        to_field_name="name",
        field_name="location__name",
    )
    concentration_unit = filters.ChoiceFilter(
        choices=AirCompoundReading.CONCENTRATION_UNITS, method="convert_to_target_unit"
    )
    longitude = filters.NumberFilter(method="filter_by_radius")
    latitude = filters.NumberFilter(method="filter_by_radius")
    radius = filters.NumberFilter(method="filter_by_radius")

    def convert_to_target_unit(self, queryset, name, value):
        return get_qs_with_converted_concentration(queryset=queryset, target_unit=value)

    def filter_by_radius(self, queryset, name, value):
        if name != "radius":
            return queryset

        longitude = float(self.data.get("longitude"))
        latitude = float(self.data.get("latitude"))
        radius = float(self.data.get("radius"))

        longitude, latitude, radius = self.validate_radius_filters(
            longitude=longitude, latitude=latitude, radius=radius
        )

        center = Point(x=longitude, y=latitude, srid=4326)

        return queryset.filter(location__coordinates__dwithin=(center, D(km=radius)))

    def validate_radius_filters(self, longitude: float, latitude: float, radius: float):
        errors = []

        try:
            longitude = self.validate_longitude(value=longitude)
        except ValidationError as e:
            errors.extend(e.detail)

        try:
            latitude = self.validate_latitude(value=latitude)
        except ValidationError as e:
            errors.extend(e.detail)

        try:
            radius = self.validate_radius(value=radius)
        except ValidationError as e:
            errors.extend(e.detail)

        if errors:
            raise ValidationError({"radius": errors})

        return longitude, latitude, radius

    @staticmethod
    def validate_latitude(value: float) -> float:
        if not -90 <= value <= 90:
            raise ValidationError("Latitude must be between -90 and 90.")
        return value

    @staticmethod
    def validate_longitude(value: float) -> float:
        if not -180 <= value <= 180:
            raise ValidationError("Longitude must be between -180 and 180.")
        return value

    @staticmethod
    def validate_radius(value: float, max_km: float = 100) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValidationError("Radius must be a valid float.")

        if value <= 0 or value > max_km:
            raise ValidationError(f"Radius must be between 0 and {max_km} km.")
        return value
