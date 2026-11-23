"""Ingresso e repasse FIFO sob o mesmo lock usado pela reserva."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import RideBooking, RideOffer, WaitlistEntry
from .booking_service import BookingService, NoSeatsAvailable, lock_booking_context


class WaitlistService:
    @staticmethod
    @transaction.atomic
    def join(*, passenger, offer_id, boarding_point_id, alighting_point_id):
        offer, passenger, confirmed = lock_booking_context(
            passenger=passenger, offer_id=offer_id,
            boarding_point_id=boarding_point_id, alighting_point_id=alighting_point_id,
        )
        existing = WaitlistEntry.objects.filter(offer=offer, passenger=passenger).first()
        if existing is not None:
            return existing
        if confirmed.count() < offer.seats:
            raise ValidationError("A carona tem vaga disponível. Solicite uma reserva.", code="seat_available")

        segment = {"boarding_point_id": boarding_point_id, "alighting_point_id": alighting_point_id}
        RideBooking(offer=offer, passenger=passenger, **segment).clean()
        return WaitlistEntry.objects.create(offer=offer, passenger=passenger, **segment)

    @staticmethod
    @transaction.atomic
    def promote_next(*, offer_id):
        offer = RideOffer.objects.select_for_update(no_key=True).get(pk=offer_id)
        if offer.status != RideOffer.Status.ABERTA or offer.departure_at <= timezone.now():
            return None
        if offer.bookings.filter(status=RideBooking.Status.CONFIRMADA).count() >= offer.seats:
            return None

        candidates = offer.waitlist_entries.select_related("passenger")
        while entry := candidates.first():
            try:
                booking = BookingService.create_booking(
                    passenger=entry.passenger, offer_id=offer.pk,
                    boarding_point_id=entry.boarding_point_id, alighting_point_id=entry.alighting_point_id,
                )
            except NoSeatsAvailable:
                return None
            except PermissionDenied:
                entry.delete()
            except ValidationError as error:
                fields = set(getattr(error, "error_dict", {}))
                if "offer_id" in fields:
                    return None
                if getattr(error, "code", None) != "already_booked" and not (
                    fields and fields <= {"boarding_point", "alighting_point"}
                ):
                    raise
                entry.delete()
            else:
                entry.delete()
                return booking
        return None
