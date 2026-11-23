"""Feature 004/T003 local — reserva serializada pela oferta, núcleo da T021."""
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from ..models import RideBooking, RideOffer


class NoSeatsAvailable(ValidationError):
    def __init__(self):
        super().__init__("Não há vagas disponíveis para esta carona.", code="no_seats")


def _already_booked():
    return ValidationError("Você já possui reserva confirmada nesta carona.", code="already_booked")


class BookingService:
    @staticmethod
    @transaction.atomic
    def create_booking(*, passenger, offer_id, boarding_point_id, alighting_point_id):
        if not getattr(passenger, "is_authenticated", False) or getattr(passenger, "pk", None) is None:
            raise PermissionDenied("Somente passageiros com vínculo ativo podem reservar.")
        errors = {}
        for name, value in (
            ("offer_id", offer_id), ("boarding_point_id", boarding_point_id),
            ("alighting_point_id", alighting_point_id),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                errors[name] = "Selecione um registro válido."
        if errors:
            raise ValidationError(errors)

        try:
            offer = RideOffer.objects.select_for_update().get(pk=offer_id)
        except RideOffer.DoesNotExist:
            raise ValidationError({"offer_id": "Selecione uma oferta existente."}) from None
        if passenger.pk == offer.driver_id:
            raise PermissionDenied("Não é permitido reservar vaga na própria carona.")

        # Ordem compartilhada com futuros cancelamentos: oferta, depois usuários por PK.
        accounts = {
            user.pk: user for user in get_user_model().objects.select_for_update().filter(
                pk__in=(passenger.pk, offer.driver_id),
            ).order_by("pk")
        }
        current_passenger = accounts.get(passenger.pk)
        if current_passenger is None or not (
            current_passenger.is_active and current_passenger.role == "PASSAGEIRO"
            and current_passenger.is_activated
        ):
            raise PermissionDenied("Somente passageiros com vínculo ativo podem reservar.")
        driver = accounts[offer.driver_id]
        now = timezone.now()
        if not (driver.is_active and driver.role == "MOTORISTA" and driver.is_activated
                and offer.departure_at > now):
            raise ValidationError({"offer_id": "Esta oferta não está disponível para reserva."})

        confirmed = RideBooking.objects.filter(offer=offer, status=RideBooking.Status.CONFIRMADA)
        if confirmed.filter(passenger=current_passenger).exists():
            raise _already_booked()
        if confirmed.count() >= offer.seats:
            raise NoSeatsAvailable()

        booking = RideBooking(
            offer=offer, passenger=current_passenger, boarding_point_id=boarding_point_id,
            alighting_point_id=alighting_point_id, status=RideBooking.Status.CONFIRMADA,
        )
        try:
            # Savepoint: traduzir apenas a restrição conhecida depois de restaurar a transação.
            with transaction.atomic():
                booking.save()
        except IntegrityError as error:
            constraint = getattr(getattr(error.__cause__, "diag", None), "constraint_name", None)
            if constraint == "booking_active_passenger_unique":
                raise _already_booked() from error
            raise
        return booking
