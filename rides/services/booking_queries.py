"""Feature 004/T004 local — leitura própria e minimização antes do template."""
from dataclasses import dataclass
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from ..models import RideBooking


@dataclass(frozen=True)
class BookingSummary:
    booking_id: int
    offer_id: int
    status: str
    departure_at: datetime
    boarding_name: str
    alighting_name: str
    counterpart_role: str
    counterpart_name: str
    vehicle_model: str
    vehicle_color: str
    vehicle_plate: str | None


class BookingQueryService:
    @staticmethod
    def list_for(*, user):
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Somente contas com vínculo ativo podem consultar reservas.")
        actor = get_user_model().objects.filter(
            pk=getattr(user, "pk", None), is_active=True, academic_status="ATIVA",
            role__in=["MOTORISTA", "PASSAGEIRO"],
        ).first()
        if actor is None:
            raise PermissionDenied("Somente contas com vínculo ativo podem consultar reservas.")
        driver_view = actor.role == "MOTORISTA"
        ownership = {"offer__driver_id": actor.pk} if driver_view else {"passenger_id": actor.pk}
        bookings = RideBooking.objects.filter(**ownership).select_related(
            "offer", "offer__driver", "passenger", "boarding_point", "alighting_point",
        ).order_by("offer__departure_at", "created_at", "id")
        results = []
        for booking in bookings:
            counterpart = booking.passenger if driver_view else booking.offer.driver
            confirmed = booking.status == RideBooking.Status.CONFIRMADA
            results.append(BookingSummary(
                booking_id=booking.pk, offer_id=booking.offer_id, status=booking.status,
                departure_at=booking.offer.departure_at, boarding_name=booking.boarding_point.name,
                alighting_name=booking.alighting_point.name,
                counterpart_role="PASSAGEIRO" if driver_view else "MOTORISTA",
                counterpart_name=counterpart.full_name if confirmed else counterpart.display_name,
                vehicle_model=booking.offer.vehicle_model, vehicle_color=booking.offer.vehicle_color,
                vehicle_plate=booking.offer.vehicle_plate if confirmed else None,
            ))
        return tuple(results)
