from rest_framework import serializers

from .models import Country, City, Airport, AirplaneType, Airplane, Crew, Route, Flight


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = City
        fields = ("id", "name", "country")


class AirportSerializer(serializers.ModelSerializer):
    closest_big_city = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "crew", "departure_time", "arrival_time")
