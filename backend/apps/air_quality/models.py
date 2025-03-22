from django.contrib.gis.db import models as gis_models
from django.core.validators import MaxValueValidator, MinValueValidator
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


class Pollutant(models.Model):
    symbol = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return self.symbol


class AirPollutantReading(models.Model):
    location = models.ForeignKey(
        to=Location, on_delete=models.CASCADE, related_name="air_pollutant_readings"
    )
    pollutant = models.ForeignKey(
        to=Pollutant, on_delete=models.CASCADE, related_name="air_pollutant_readings"
    )
    concentration = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(300)],
        help_text="Concentration of the pollutant",
    )
    concentration_unit = models.CharField(
        help_text="Concentration unit of the pollutant",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
