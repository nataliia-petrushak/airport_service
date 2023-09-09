from datetime import datetime

from django.db.models import F, Count, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import (
    Country,
    City,
    Airport,
    Airplane,
    AirplaneType,
    Route,
    Crew,
    Flight,
    Order,
)
from .permisions import IsAdminOrIfAuthenticatedReadOnly
from .serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
    AirportSerializer,
    AirportListSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    CrewSerializer,
    CrewListSerializer,
    CrewImageSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class CountryViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CityViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = City.objects.select_related("country")
    serializer_class = CitySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer

        return self.serializer_class


class AirportViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = Airport.objects.select_related("closest_big_city")
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer

        return self.serializer_class


class AirplaneTypeViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        return self.serializer_class


class CrewViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer

        if self.action == "upload_image":
            return CrewImageSerializer

        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        crew = self.get_object()
        serializer = self.get_serializer(crew, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.select_related(
        "source",
        "destination",
    )
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer

    def get_queryset(self):
        country_from = self.request.query_params.get("country_from")
        country_to = self.request.query_params.get("country_to")
        city_from = self.request.query_params.get("city_from")
        city_to = self.request.query_params.get("city_to")
        route = self.request.query_params.get("route")

        if country_from:
            self.queryset = self.queryset.filter(
                source__closest_big_city__country__name__icontains=country_from
            )

        if country_to:
            self.queryset = self.queryset.filter(
                destination__closest_big_city__country__name__icontains=country_to
            )

        if city_from:
            self.queryset = self.queryset.filter(
                source__closest_big_city__name__icontains=city_from
            )

        if city_to:
            self.queryset = self.queryset.filter(
                source__closest_big_city__name__icontains=city_to
            )

        if route:
            route = route.split("-")
            self.queryset = self.queryset.filter(
                Q(source__closest_big_city__name__icontains=route[0]),
                Q(destination__closest_big_city__name__icontains=route[-1]),
            )
        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="country_from",
                description="Filter by country of departure (ex. ?country_from=Estonia)",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="country_to",
                description="Filter by country of destination (ex. ?country_to=France)",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="city_from",
                description="Filter by city of departure (ex. ?city_from=Tallinn)",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="city_to",
                description="Filter by city of destination (ex. ?city_to=Paris)",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="route",
                description="Filter by city of departure & city of destination (ex. ?route=Tallinn-Paris)",
                type=OpenApiTypes.STR
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Flight.objects.select_related(
            "route",
            "airplane",
            "route__destination__closest_big_city",
            "route__source__closest_big_city",
        )
        .prefetch_related("crews")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    def get_queryset(self):
        airport_from = self.request.query_params.get("airport_from")
        airport_to = self.request.query_params.get("airport_to")
        date = self.request.query_params.get("date")

        if airport_from:
            self.queryset = self.queryset.filter(route__source__name__icontains=airport_from)

        if airport_to:
            self.queryset = self.queryset.filter(route__destination__name__icontains=airport_to)

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            self.queryset = self.queryset.filter(departure_time__date=date)

        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="airport_from",
                description="Filter by airport of departure (ex. ?airport_from=Tallinn Airport)",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="airport_to",
                description="Filter by airport of destination (ex. ?airport_to=Riga)",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="date",
                description="Filter by date of departure (ex. ?date=2023-09-12)",
                type=OpenApiTypes.DATE
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.prefetch_related("tickets__flight__route")
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
