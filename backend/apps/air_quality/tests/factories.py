import random

import factory
from apps.air_quality.models import AirCompoundReading, Compound, Location, Tag
from django.contrib.gis.geos import Point


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"Tag {n}")


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Sequence(lambda n: f"Location {n}")
    coordinates = factory.LazyFunction(lambda: Point(0, 0))

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class CompoundFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Compound

    symbol = factory.Sequence(lambda n: f"CO{n}")
    full_name = factory.Sequence(lambda n: f"Carbon Monoxide {n}")


class AirCompoundReadingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AirCompoundReading

    compound = factory.SubFactory(CompoundFactory)
    location = factory.SubFactory(LocationFactory)
    entered_concentration_value = factory.Faker("pyfloat", min_value=0.1, max_value=100)
    entered_concentration_unit = factory.LazyFunction(
        lambda: random.choice(["ug_m3", "mg_m3", "ppm", "ppb"])
    )
