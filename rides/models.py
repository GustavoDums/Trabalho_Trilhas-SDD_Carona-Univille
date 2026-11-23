"""Feature 002 / T002 local / roadmap T013 — modelos de oferta e itinerário."""

from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


def require_integer(value, field):
    """Impede truncamento silencioso antes de IntegerField.to_python()."""
    if value is None:
        return
    try:
        number = Decimal(str(value))
        valid = not isinstance(value, bool) and number.is_finite() and number == number.to_integral_value()
    except (InvalidOperation, ValueError):
        valid = False
    if not valid:
        raise ValidationError({field: "Informe um número inteiro."})


class ValidatedModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class RoutePoint(ValidatedModel):
    code = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=100)

    def clean_fields(self, exclude=None):
        if isinstance(self.name, str):
            self.name = self.name.strip()
        super().clean_fields(exclude=exclude)


class RideOffer(ValidatedModel):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ride_offers")
    origin = models.ForeignKey(RoutePoint, on_delete=models.PROTECT, related_name="origin_offers")
    destination = models.ForeignKey(RoutePoint, on_delete=models.PROTECT, related_name="destination_offers")
    departure_at = models.DateTimeField()
    seats = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    vehicle_model = models.CharField(max_length=100)
    vehicle_color = models.CharField(max_length=50)
    vehicle_plate = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["departure_at", "created_at", "id"]
        indexes = [models.Index(fields=["driver", "departure_at"], name="ride_driver_departure_idx")]
        constraints = [
            models.CheckConstraint(condition=models.Q(seats__gte=1), name="ride_seats_positive"),
            models.CheckConstraint(condition=~models.Q(origin=models.F("destination")), name="ride_endpoints_distinct"),
        ]

    def clean_fields(self, exclude=None):
        exclude = exclude or []
        for field in ("vehicle_model", "vehicle_color", "vehicle_plate"):
            value = getattr(self, field)
            if isinstance(value, str):
                setattr(self, field, value.strip().upper() if field == "vehicle_plate" else value.strip())
        if "seats" not in exclude:
            require_integer(self.seats, "seats")
        if "departure_at" not in exclude and isinstance(self.departure_at, datetime) and timezone.is_naive(self.departure_at):
            raise ValidationError({"departure_at": "Informe data e horário com fuso definido."})
        super().clean_fields(exclude=exclude)

    def clean(self):
        super().clean()
        errors = {}
        if self.origin_id and self.origin_id == self.destination_id:
            errors["destination"] = "Origem e destino devem ser distintos."
        if self._state.adding:
            if self.driver_id:
                eligible = get_user_model().objects.filter(
                    pk=self.driver_id, is_active=True, role="MOTORISTA", academic_status="ATIVA",
                ).exists()
                if not eligible:
                    errors["driver"] = "Somente motorista com vínculo ativo pode criar oferta."
            if isinstance(self.departure_at, datetime) and timezone.is_aware(self.departure_at):
                if self.departure_at <= timezone.now():
                    errors["departure_at"] = "A saída deve ser estritamente futura."
        if errors:
            raise ValidationError(errors)


class Waypoint(ValidatedModel):
    offer = models.ForeignKey(RideOffer, on_delete=models.CASCADE, related_name="waypoints")
    point = models.ForeignKey(RoutePoint, on_delete=models.PROTECT)
    position = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["offer", "position"], name="waypoint_offer_position_unique"),
            models.UniqueConstraint(fields=["offer", "point"], name="waypoint_offer_point_unique"),
            models.CheckConstraint(condition=models.Q(position__gte=1), name="waypoint_position_positive"),
        ]

    def clean_fields(self, exclude=None):
        if "position" not in (exclude or []):
            require_integer(self.position, "position")
        super().clean_fields(exclude=exclude)

    def clean(self):
        super().clean()
        if self.offer_id and self.point_id:
            endpoints = RideOffer.objects.filter(pk=self.offer_id).values_list("origin_id", "destination_id").first()
            if endpoints and self.point_id in endpoints:
                raise ValidationError({"point": "A parada deve ser distinta da origem e do destino."})
