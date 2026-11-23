"""Materializa a janela local de uma regra com publicação atômica."""
from datetime import date, datetime, timedelta, timezone as utc_timezone
from typing import NamedTuple
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from reviews.services.conduct_service import require_unsuspended

from ..models import RecurringRideOccurrence, RecurringRideRule
from . import publish_offer

HORIZON_DAYS = 16


class GenerationResult(NamedTuple):
    created_dates: tuple[date, ...]
    existing_dates: tuple[date, ...]


class RecurringRideService:
    @staticmethod
    @transaction.atomic
    def generate(*, rule_id, driver, clock=None):
        if not getattr(driver, "is_authenticated", False) or getattr(driver, "pk", None) is None:
            raise PermissionDenied("Somente o motorista titular pode gerar caronas da regra.")
        if type(rule_id) is not int or rule_id <= 0:
            raise ValidationError({"rule_id": "Selecione uma regra válida."})
        rule = RecurringRideRule.objects.select_for_update(no_key=True).filter(
            pk=rule_id, driver_id=driver.pk,
        ).first()
        if rule is None:
            raise PermissionDenied("Somente o motorista titular pode gerar caronas da regra.")
        owner = get_user_model().objects.select_for_update(no_key=True).get(pk=rule.driver_id)
        if not (owner.is_active and owner.is_activated and owner.role == "MOTORISTA"):
            raise PermissionDenied("Somente motoristas com vínculo ativo podem gerar caronas.")
        if not rule.active:
            return GenerationResult((), ())

        instant = (clock or timezone.now)()
        if not isinstance(instant, datetime) or timezone.is_naive(instant):
            raise ValidationError("Informe um instante de referência com fuso horário definido.")
        instant = instant.astimezone(utc_timezone.utc)
        require_unsuspended(owner.pk, at=instant)
        local_zone = ZoneInfo(rule.timezone)
        first_date = instant.astimezone(local_zone).date()
        last_date = first_date + timedelta(days=HORIZON_DAYS - 1)
        existing_occurrence_dates = set(
            rule.occurrences.filter(local_date__range=(first_date, last_date)).values_list("local_date", flat=True),
        )
        points = [stop.point for stop in rule.stops.select_related("point")]
        offer_data = {
            "origin": rule.origin, "destination": rule.destination, "seats": rule.seats,
            "vehicle_model": rule.vehicle_model, "vehicle_color": rule.vehicle_color,
            "vehicle_plate": rule.vehicle_plate,
        }

        created_dates, existing_dates = [], []
        for offset in range(HORIZON_DAYS):
            local_date = first_date + timedelta(days=offset)
            if local_date.weekday() not in rule.weekdays:
                continue
            departure_at = datetime.combine(local_date, rule.local_time, tzinfo=local_zone)
            if departure_at <= instant:
                continue
            if local_date in existing_occurrence_dates:
                existing_dates.append(local_date)
                continue
            offer = publish_offer(driver=owner, data=dict(offer_data, departure_at=departure_at), points=points)
            RecurringRideOccurrence.objects.create(rule=rule, local_date=local_date, offer=offer)
            created_dates.append(local_date)
        return GenerationResult(tuple(created_dates), tuple(existing_dates))
