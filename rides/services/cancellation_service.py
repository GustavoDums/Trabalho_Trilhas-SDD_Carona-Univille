"""Feature 005/T002–T004 — política temporal e cancelamentos atômicos."""
from datetime import datetime, timedelta, timezone as dt_timezone

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import CancellationRecord, RideBooking, RideOffer


class CancellationRefused(ValidationError):
    def __init__(self):
        super().__init__(
            "Não é possível cancelar a partir do horário de saída da origem.",
            code="departure_reached",
        )


class CancellationPolicy:
    DEADLINES = {"PASSAGEIRO": timedelta(hours=2), "MOTORISTA": timedelta(hours=4)}

    @classmethod
    def classify(cls, *, role, departure_at, at):
        if role not in cls.DEADLINES:
            raise ValidationError("Papel inválido para cancelamento.", code="invalid_role")
        if any(not isinstance(value, datetime) or timezone.is_naive(value)
               for value in (departure_at, at)):
            raise ValidationError("Informe instantes válidos com fuso definido.", code="invalid_time")
        departure = departure_at.astimezone(dt_timezone.utc)
        instant = at.astimezone(dt_timezone.utc)
        if instant >= departure:
            raise CancellationRefused()
        return (CancellationRecord.Classification.TEMPESTIVO
                if departure-instant >= cls.DEADLINES[role] else CancellationRecord.Classification.TARDIO)


class CancellationService:
    @staticmethod
    @transaction.atomic
    def cancel_booking(*, user, booking_id, clock=None):
        if not getattr(user, "is_authenticated", False) or getattr(user, "pk", None) is None:
            raise PermissionDenied("Somente o passageiro titular ativo pode cancelar.")
        if isinstance(booking_id, bool) or not isinstance(booking_id, int) or booking_id <= 0:
            raise ValidationError({"booking_id": "Selecione uma reserva válida."})
        reference = RideBooking.objects.filter(pk=booking_id).values("offer_id").first()
        if reference is None:
            raise ValidationError({"booking_id": "Selecione uma reserva existente."})
        offer = RideOffer.objects.select_for_update().get(pk=reference["offer_id"])
        accounts = {
            actor.pk: actor for actor in get_user_model().objects.select_for_update().filter(
                pk__in=(user.pk, offer.driver_id),
            ).order_by("pk")
        }
        actor = accounts.get(user.pk)
        if actor is None or not (actor.is_active and actor.role == "PASSAGEIRO" and actor.is_activated):
            raise PermissionDenied("Somente o passageiro titular ativo pode cancelar.")
        booking = RideBooking.objects.select_for_update().filter(
            pk=booking_id, offer_id=offer.pk,
        ).first()
        if booking is None:
            raise ValidationError({"booking_id": "A reserva não está disponível."})
        if booking.passenger_id != actor.pk:
            raise PermissionDenied("Somente o passageiro titular ativo pode cancelar.")
        if booking.status == RideBooking.Status.CANCELADA:
            return booking
        now = (clock or timezone.now)()
        classification = CancellationPolicy.classify(
            role=actor.role, departure_at=offer.departure_at, at=now,
        )
        booking.status = RideBooking.Status.CANCELADA
        booking.cancelled_at = now
        booking.save(update_fields=["status", "cancelled_at", "updated_at"])
        CancellationRecord.objects.create(
            actor=actor, offer=offer, booking=booking,
            occurred_at=now, classification=classification,
        )
        return booking

    @staticmethod
    @transaction.atomic
    def cancel_offer(*, user, offer_id, clock=None):
        """Fecha oferta própria e suas reservas confirmadas no mesmo commit."""
        if not getattr(user, "is_authenticated", False) or getattr(user, "pk", None) is None:
            raise PermissionDenied("Somente o motorista titular ativo pode cancelar.")
        if isinstance(offer_id, bool) or not isinstance(offer_id, int) or offer_id <= 0:
            raise ValidationError({"offer_id": "Selecione uma oferta válida."})
        offer = RideOffer.objects.select_for_update().filter(pk=offer_id).first()
        if offer is None:
            raise ValidationError({"offer_id": "Selecione uma oferta existente."})
        accounts = {
            actor.pk: actor for actor in get_user_model().objects.select_for_update().filter(
                pk__in=(user.pk, offer.driver_id),
            ).order_by("pk")
        }
        actor = accounts.get(user.pk)
        if (actor is None or actor.pk != offer.driver_id
                or not (actor.is_active and actor.role == "MOTORISTA" and actor.is_activated)):
            raise PermissionDenied("Somente o motorista titular ativo pode cancelar.")
        if offer.status == RideOffer.Status.CANCELADA:
            return offer
        bookings = list(RideBooking.objects.select_for_update().filter(
            offer=offer, status=RideBooking.Status.CONFIRMADA,
        ).order_by("pk"))
        now = (clock or timezone.now)()
        classification = CancellationPolicy.classify(
            role=actor.role, departure_at=offer.departure_at, at=now,
        )
        offer.status = RideOffer.Status.CANCELADA
        offer.cancelled_at = now
        offer.save(update_fields=["status", "cancelled_at"])
        for booking in bookings:
            booking.status = RideBooking.Status.CANCELADA
            booking.cancelled_at = now
            booking.save(update_fields=["status", "cancelled_at", "updated_at"])
        # Um evento de oferta representa o lote; não atribuir cancelamentos ao passageiro.
        CancellationRecord.objects.create(
            actor=actor, offer=offer, booking=None,
            occurred_at=now, classification=classification,
        )
        return offer
