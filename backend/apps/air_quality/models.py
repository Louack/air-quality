from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
    )

    def __str__(self):
        return self.name


class Location(gis_models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
    )
    coordinates = gis_models.PointField(geography=True, srid=4326)
    tags = models.ManyToManyField(to=Tag, related_name="anemometers", blank=True)

    def __str__(self):
        return self.name


class Compound(models.Model):
    symbol = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=100)
    molecular_weight = models.FloatField(null=True, blank=True)
    is_gaseous = models.BooleanField(default=False)

    def __str__(self):
        return self.symbol


class AirCompoundReading(models.Model):
    CONCENTRATION_UNITS = (
        ("ug_m3", "Micrograms per cubic meter"),
        ("mg_m3", "Milligrams per cubic meter"),
        ("ppm", "Parts per million"),
        ("ppb", "Parts per billion"),
    )
    location = models.ForeignKey(
        to=Location, on_delete=models.CASCADE, related_name="air_readings"
    )
    compound = models.ForeignKey(
        to=Compound, on_delete=models.CASCADE, related_name="air_readings"
    )
    entered_concentration_value = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Entered concentration value of the target compound",
    )
    entered_concentration_unit = models.CharField(
        max_length=10,
        choices=CONCENTRATION_UNITS,
        help_text="Concentration of the entered concentration value",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
