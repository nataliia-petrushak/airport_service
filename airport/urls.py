from rest_framework import routers
from .views import CountryViewSet, CityViewSet, AirportViewSet

router = routers.DefaultRouter()
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)

urlpatterns = router.urls

app_name = "airport"
