from rest_framework import serializers


class AirCompoundRadiusResponseSerializer(serializers.Serializer):
    min_concentration = serializers.FloatField()
    max_concentration = serializers.FloatField()
    mean_concentration = serializers.FloatField()
