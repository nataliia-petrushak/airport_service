from django.contrib import admin

from .models import Country, City, Airport, Route, AirplaneType, Airplane, Crew, Flight


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "country"]


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ["name", "closest_big_city"]
    list_filter = ["closest_big_city"]
    search_fields = ["name"]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["source", "destination", "distance"]
    list_filter = ["source"]


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ["name", "rows", "seats_in_row", "airplane_type"]
    list_filter = ["airplane_type"]
    search_fields = ["name"]


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name"]


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ["route", "airplane", "departure_time", "arrival_time"]
    list_filter = ["route"]


admin.site.register(Country)
admin.site.register(AirplaneType)
