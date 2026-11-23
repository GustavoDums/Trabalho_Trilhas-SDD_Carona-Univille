"""Feature 002 / T002 local / roadmap T013 — modelos de oferta e itinerário."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

RECURRING_TIMEZONE = "America/Sao_Paulo"


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


def require_aware_datetime(value):
    if timezone.is_naive(value):
        raise ValidationError("Informe data e horário com fuso definido.")


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
    class Status(models.TextChoices):
        ABERTA = "ABERTA", "Aberta"
        CANCELADA = "CANCELADA", "Cancelada"

    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ride_offers")
    origin = models.ForeignKey(RoutePoint, on_delete=models.PROTECT, related_name="origin_offers")
    destination = models.ForeignKey(RoutePoint, on_delete=models.PROTECT, related_name="destination_offers")
    departure_at = models.DateTimeField()
    status = models.CharField(max_length=9, choices=Status.choices, default=Status.ABERTA)
    cancelled_at = models.DateTimeField(null=True, blank=True, validators=[require_aware_datetime])
    completed_at = models.DateTimeField(null=True, blank=True, validators=[require_aware_datetime])
    seats = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    vehicle_model = models.CharField(max_length=100)
    vehicle_color = models.CharField(max_length=50)
    vehicle_plate = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["departure_at", "created_at", "id"]
        indexes = [models.Index(fields=["driver", "departure_at"], name="ride_driver_departure_idx")]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(completed_at__isnull=True) | (
                    models.Q(completed_at__gte=models.F("departure_at")) & models.Q(status="ABERTA")
                ), name="ride_completion_valid",
            ),
            models.CheckConstraint(condition=models.Q(status__in=["ABERTA", "CANCELADA"]), name="ride_offer_status_valid"),
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


class RideBooking(ValidatedModel):
    """Feature 004/T002 local — estrutura; operação transacional pertence à T003."""

    class Status(models.TextChoices):
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        CANCELADA = "CANCELADA", "Cancelada"

    offer = models.ForeignKey(RideOffer, on_delete=models.PROTECT, related_name="bookings")
    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ride_bookings",
    )
    boarding_point = models.ForeignKey(
        RoutePoint, on_delete=models.PROTECT, related_name="boarding_bookings",
    )
    alighting_point = models.ForeignKey(
        RoutePoint, on_delete=models.PROTECT, related_name="alighting_bookings",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONFIRMADA)
    cancelled_at = models.DateTimeField(null=True, blank=True, validators=[require_aware_datetime])
    no_show_at = models.DateTimeField(null=True, blank=True, validators=[require_aware_datetime])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "passenger"], condition=models.Q(status="CONFIRMADA"),
                name="booking_active_passenger_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=["CONFIRMADA", "CANCELADA"]),
                name="booking_status_valid",
            ),
            models.CheckConstraint(
                condition=~models.Q(boarding_point=models.F("alighting_point")),
                name="booking_points_distinct",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}
        offer = RideOffer.objects.filter(pk=self.offer_id).values(
            "driver_id", "origin_id", "destination_id",
        ).first() if self.offer_id else None
        if offer and self.passenger_id == offer["driver_id"]:
            errors["passenger"] = "Não é permitido reservar vaga na própria carona."
        elif self._state.adding and self.passenger_id:
            eligible = get_user_model().objects.filter(
                pk=self.passenger_id, role="PASSAGEIRO", academic_status="ATIVA", is_active=True,
            ).exists()
            if not eligible:
                errors["passenger"] = "Somente passageiros com vínculo ativo podem reservar."

        if offer and self.boarding_point_id and self.alighting_point_id:
            itinerary = [
                offer["origin_id"],
                *Waypoint.objects.filter(offer_id=self.offer_id).order_by("position").values_list(
                    "point_id", flat=True,
                ),
                offer["destination_id"],
            ]
            if len(set(itinerary)) != len(itinerary):
                errors["boarding_point"] = "O itinerário da oferta contém pontos repetidos."
            else:
                if self.boarding_point_id not in itinerary:
                    errors["boarding_point"] = "O embarque deve pertencer ao itinerário da oferta."
                if self.alighting_point_id not in itinerary:
                    errors["alighting_point"] = "O desembarque deve pertencer ao itinerário da oferta."
                if (self.boarding_point_id in itinerary and self.alighting_point_id in itinerary
                        and itinerary.index(self.boarding_point_id) >= itinerary.index(self.alighting_point_id)):
                    errors["alighting_point"] = "O desembarque deve estar depois do embarque."
        if errors:
            raise ValidationError(errors)


class WaitlistEntry(models.Model):
    offer = models.ForeignKey(RideOffer, on_delete=models.PROTECT, related_name="waitlist_entries")
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                  related_name="waitlist_entries")
    boarding_point = models.ForeignKey(RoutePoint, on_delete=models.PROTECT,
                                       related_name="waitlist_boardings")
    alighting_point = models.ForeignKey(RoutePoint, on_delete=models.PROTECT,
                                        related_name="waitlist_alightings")

    class Meta:
        ordering = ("pk",)
        indexes = [models.Index(fields=("offer", "id"), name="waitlist_offer_fifo_idx")]
        constraints = [
            models.UniqueConstraint(fields=("offer", "passenger"), name="waitlist_passenger_unique"),
            models.CheckConstraint(condition=~models.Q(boarding_point=models.F("alighting_point")),
                                   name="waitlist_points_distinct"),
        ]


class CancellationRecord(ValidatedModel):
    """Feature 005/T002 — um evento por transição efetiva, sem penalidade numérica."""

    class Classification(models.TextChoices):
        TEMPESTIVO = "TEMPESTIVO", "Tempestivo"
        TARDIO = "TARDIO", "Tardio"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cancellation_records",
    )
    offer = models.ForeignKey(RideOffer, on_delete=models.PROTECT, related_name="cancellation_records")
    booking = models.ForeignKey(
        RideBooking, on_delete=models.PROTECT, null=True, blank=True, related_name="cancellation_records",
    )
    occurred_at = models.DateTimeField(validators=[require_aware_datetime])
    classification = models.CharField(max_length=10, choices=Classification.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(classification__in=["TEMPESTIVO", "TARDIO"]),
                name="cancellation_class_valid",
            ),
            models.UniqueConstraint(
                fields=["booking"], condition=models.Q(booking__isnull=False),
                name="cancellation_booking_unique",
            ),
            models.UniqueConstraint(
                fields=["offer"], condition=models.Q(booking__isnull=True),
                name="cancellation_offer_unique",
            ),
        ]

    def clean(self):
        super().clean()
        if self.booking_id:
            offer_id = RideBooking.objects.filter(pk=self.booking_id).values_list("offer_id", flat=True).first()
            if offer_id is not None and offer_id != self.offer_id:
                raise ValidationError({"offer": "A reserva deve pertencer à oferta auditada."})


class RecurringRideRule(ValidatedModel):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                               related_name="recurring_ride_rules")
    origin = models.ForeignKey(RoutePoint, on_delete=models.PROTECT, related_name="origin_recurring_rules")
    destination = models.ForeignKey(RoutePoint, on_delete=models.PROTECT, related_name="destination_recurring_rules")
    weekdays = ArrayField(models.PositiveSmallIntegerField(), size=7)
    local_time = models.TimeField()
    timezone = models.CharField(max_length=64, choices=[(RECURRING_TIMEZONE, RECURRING_TIMEZONE)],
                                default=RECURRING_TIMEZONE)
    seats = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    vehicle_model = models.CharField(max_length=100)
    vehicle_color = models.CharField(max_length=50)
    vehicle_plate = models.CharField(max_length=20)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~models.Q(origin=models.F("destination")),
                                   name="recurring_rule_endpoints_distinct"),
            models.CheckConstraint(condition=models.Q(seats__gte=1), name="recurring_rule_seats_positive"),
            models.CheckConstraint(condition=models.Q(weekdays__len__range=(1, 7),
                                                       weekdays__contained_by=[0, 1, 2, 3, 4, 5, 6]),
                                   name="recurring_rule_weekdays_valid"),
            models.CheckConstraint(condition=models.Q(timezone=RECURRING_TIMEZONE),
                                   name="recurring_rule_timezone_valid"),
        ]

    def clean_fields(self, exclude=None):
        excluded = exclude or ()
        if "weekdays" not in excluded:
            days = self.weekdays
            if (not isinstance(days, (list, tuple)) or not days
                    or any(type(day) is not int or not 0 <= day <= 6 for day in days)
                    or len(set(days)) != len(days)):
                raise ValidationError({"weekdays": "Escolha dias distintos entre segunda e domingo."})
            self.weekdays = sorted(days)
        if "local_time" not in excluded and getattr(self.local_time, "tzinfo", None) is not None:
            raise ValidationError({"local_time": "Informe apenas o horário local, sem fuso horário."})
        if "seats" not in excluded:
            require_integer(self.seats, "seats")
        for field in ("vehicle_model", "vehicle_color", "vehicle_plate"):
            value = getattr(self, field)
            if isinstance(value, str):
                setattr(self, field, value.strip().upper() if field == "vehicle_plate" else value.strip())
        super().clean_fields(exclude=exclude)

    def clean(self):
        super().clean()
        if self._state.adding and self.driver_id and not get_user_model().objects.filter(
            pk=self.driver_id, role="MOTORISTA", academic_status="ATIVA", is_active=True,
        ).exists():
            raise ValidationError({"driver": "Somente motorista com vínculo ativo pode cadastrar recorrência."})


class RecurringRideStop(ValidatedModel):
    rule = models.ForeignKey(RecurringRideRule, on_delete=models.CASCADE, related_name="stops")
    point = models.ForeignKey(RoutePoint, on_delete=models.PROTECT, related_name="recurring_stops")
    position = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["rule", "position"], name="recurring_stop_position_unique"),
            models.UniqueConstraint(fields=["rule", "point"], name="recurring_stop_point_unique"),
            models.CheckConstraint(condition=models.Q(position__gte=1), name="recurring_stop_position_positive"),
        ]

    def clean_fields(self, exclude=None):
        if "position" not in (exclude or ()):
            require_integer(self.position, "position")
        super().clean_fields(exclude=exclude)

    def clean(self):
        super().clean()
        endpoints = RecurringRideRule.objects.filter(pk=self.rule_id).values_list(
            "origin_id", "destination_id",
        ).first()
        if endpoints and self.point_id in endpoints:
            raise ValidationError({"point": "A parada deve ser distinta da origem e do destino."})


class RecurringRideOccurrence(ValidatedModel):
    rule = models.ForeignKey(RecurringRideRule, on_delete=models.PROTECT, related_name="occurrences")
    local_date = models.DateField()
    offer = models.OneToOneField(RideOffer, on_delete=models.PROTECT, related_name="recurring_occurrence")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["rule", "local_date"], name="recurring_occurrence_rule_date_unique"),
        ]

    def clean(self):
        super().clean()
        driver_id = RecurringRideRule.objects.filter(pk=self.rule_id).values_list("driver_id", flat=True).first()
        offer = RideOffer.objects.filter(pk=self.offer_id).values_list("driver_id", "departure_at").first()
        if offer is not None:
            offer_driver_id, departure_at = offer
            if driver_id != offer_driver_id:
                raise ValidationError({"offer": "A oferta deve pertencer ao motorista da regra."})
            if departure_at.astimezone(ZoneInfo(RECURRING_TIMEZONE)).date() != self.local_date:
                raise ValidationError({"local_date": "Informe a data local de partida da oferta."})
