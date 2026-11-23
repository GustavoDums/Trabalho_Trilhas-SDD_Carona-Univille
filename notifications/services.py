"""Avisos internos persistidos na transação da operação de origem."""
from .models import Notification


class NotificationService:
    @staticmethod
    def booking_confirmed(booking):
        recipients = {booking.passenger_id, booking.offer.driver_id}
        Notification.objects.bulk_create([
            Notification(recipient_id=recipient_id, booking=booking, kind=Notification.Kind.BOOKING_CONFIRMED)
            for recipient_id in sorted(recipients)
        ], ignore_conflicts=True)

    @staticmethod
    def cancellation_recorded(event, *, affected_passenger_ids=()):
        recipients = {event.offer.driver_id}
        if event.booking_id is not None:
            kind = Notification.Kind.BOOKING_CANCELLED
            recipients.add(event.actor_id)
        else:
            kind = Notification.Kind.OFFER_CANCELLED
            recipients.update(affected_passenger_ids)
        Notification.objects.bulk_create([
            Notification(recipient_id=recipient_id, cancellation=event, kind=kind)
            for recipient_id in sorted(recipients)
        ], ignore_conflicts=True)
