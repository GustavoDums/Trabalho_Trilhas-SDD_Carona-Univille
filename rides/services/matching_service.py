"""Feature 003/T002 local — matching read-only por rota e saída da origem."""
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Prefetch
from django.utils import timezone

from ..models import RideOffer, RoutePoint, Waypoint

WINDOW = timedelta(minutes=30)


@dataclass(frozen=True)
class SearchQuery:
    boarding_id: int
    alighting_id: int
    desired_at: datetime

    def __post_init__(self):
        errors = {}
        for name in ("boarding_id", "alighting_id"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                errors[name] = "Selecione um ponto válido do catálogo."
        if not errors and self.boarding_id == self.alighting_id:
            errors["alighting_id"] = "Embarque e desembarque devem ser distintos."
        if not isinstance(self.desired_at, datetime) or timezone.is_naive(self.desired_at):
            errors["desired_at"] = "Informe data e horário com fuso definido."
        if errors:
            raise ValidationError(errors)


@dataclass(frozen=True)
class SearchResult:
    offer_id: int
    driver_display_name: str
    itinerary: tuple[str, ...]
    departure_at: datetime
    seats: int
    vehicle_model: str
    vehicle_color: str


class MatchingService:
    @staticmethod
    def _itinerary(offer):
        return (offer.origin, *(stop.point for stop in offer.waypoints.all()), offer.destination)

    @classmethod
    def route_matches(cls, offer, query):
        ids = [point.pk for point in cls._itinerary(offer)]
        if len(set(ids)) != len(ids):
            return False
        return (query.boarding_id in ids and query.alighting_id in ids
                and ids.index(query.boarding_id) < ids.index(query.alighting_id))

    @staticmethod
    def time_matches(departure_at, desired_at):
        return desired_at - WINDOW <= departure_at <= desired_at + WINDOW

    @classmethod
    def search(cls, *, passenger, query):
        if not get_user_model().objects.filter(
            pk=getattr(passenger, "pk", None), role="PASSAGEIRO",
            academic_status="ATIVA", is_active=True,
        ).exists():
            raise PermissionDenied("Somente passageiros com vínculo ativo podem buscar.")
        if not isinstance(query, SearchQuery):
            raise ValidationError("Informe uma consulta de busca válida.")
        existing = set(RoutePoint.objects.filter(
            pk__in=(query.boarding_id, query.alighting_id)).values_list("pk", flat=True))
        errors = {field: "Selecione um ponto existente do catálogo."
                  for field in ("boarding_id", "alighting_id")
                  if getattr(query, field) not in existing}
        if errors:
            raise ValidationError(errors)

        now = timezone.now()
        candidates = RideOffer.objects.filter(
            departure_at__gt=now,
            departure_at__gte=query.desired_at - WINDOW,
            departure_at__lte=query.desired_at + WINDOW,
            seats__gt=0,
            driver__role="MOTORISTA", driver__academic_status="ATIVA", driver__is_active=True,
        ).select_related("driver", "origin", "destination").prefetch_related(
            Prefetch("waypoints", queryset=Waypoint.objects.select_related("point").order_by("position"))
        ).order_by("departure_at", "created_at", "id")

        return tuple(
            SearchResult(
                offer_id=offer.pk, driver_display_name=offer.driver.display_name,
                itinerary=tuple(point.name for point in cls._itinerary(offer)),
                departure_at=offer.departure_at, seats=offer.seats,
                vehicle_model=offer.vehicle_model, vehicle_color=offer.vehicle_color,
            )
            for offer in candidates if cls.route_matches(offer, query)
        )

