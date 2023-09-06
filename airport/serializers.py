from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    Country,
    City,
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
    Order,
    Ticket,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class CityListSerializer(CitySerializer):
    country = serializers.SlugRelatedField(slug_field="name", read_only=True)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(slug_field="name", read_only=True)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class RouteDetailSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

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
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "capacity")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(slug_field="name", read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewListSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "image")


class CrewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "image")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "crews", "departure_time", "arrival_time")


class FlightListSerializer(FlightSerializer):
    route = serializers.CharField(source="route.__str__", read_only=True)
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane_name",
            "airplane_capacity",
            "tickets_available",
            "departure_time",
            "arrival_time",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"], attrs["seat"], attrs["flight"].airplane, ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    crews = CrewSerializer(many=True, read_only=True)
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    taken_places = TicketSeatsSerializer(source="tickets", many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crews",
            "departure_time",
            "arrival_time",
            "taken_places",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(allow_null=False, many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Order
        fields = ("id", "user", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
