from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        BOOKING_CONFIRMED = "BOOKING_CONFIRMED", "Reserva confirmada"
        BOOKING_CANCELLED = "BOOKING_CANCELLED", "Reserva cancelada"
        OFFER_CANCELLED = "OFFER_CANCELLED", "Oferta cancelada"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                  related_name="notifications")
    booking = models.ForeignKey("rides.RideBooking", on_delete=models.PROTECT, null=True, blank=True,
                                related_name="notifications")
    cancellation = models.ForeignKey("rides.CancellationRecord", on_delete=models.PROTECT, null=True, blank=True,
                                     related_name="notifications")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        indexes = [
            models.Index(fields=["recipient", "-created_at", "-id"], name="notice_recipient_time_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(kind="BOOKING_CONFIRMED", booking__isnull=False, cancellation__isnull=True)
                    | models.Q(kind__in=["BOOKING_CANCELLED", "OFFER_CANCELLED"], booking__isnull=True,
                               cancellation__isnull=False)
                ),
                name="notice_kind_origin_valid",
            ),
            models.UniqueConstraint(
                fields=["recipient", "booking"], condition=models.Q(booking__isnull=False),
                name="notice_recipient_booking_once",
            ),
            models.UniqueConstraint(
                fields=["recipient", "cancellation"], condition=models.Q(cancellation__isnull=False),
                name="notice_recipient_cancellation_once",
            ),
        ]
