from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} ({self.country.name})"


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} ({self.closest_big_city}, {self.closest_big_city.country.name})"


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE)
    distance = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.source} - {self.destination} ({self.distance}km)"
