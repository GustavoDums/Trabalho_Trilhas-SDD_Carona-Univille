"""Feature 005/T002 — roadmap T024; REQ-007/REQ-017, relógio controlado."""
from datetime import datetime, timedelta, timezone as dt_timezone
from importlib import import_module
from unittest.mock import Mock

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, transaction

from rides.models import RideBooking, RideOffer

DEPARTURE = datetime(2030, 1, 4, 0, 30, tzinfo=dt_timezone.utc)


def api():
    return import_module("rides.services.cancellation_service")


def records():
    return apps.get_model("rides", "CancellationRecord")


@pytest.mark.parametrize("role,seconds", [("PASSAGEIRO", 7200), ("MOTORISTA", 14400)])
@pytest.mark.parametrize("offset,expected", [(1, "TEMPESTIVO"), (0, "TEMPESTIVO"), (-1, "TARDIO")])
def test_policy_second_boundaries(role, seconds, offset, expected):
    assert api().CancellationPolicy.classify(
        role=role, departure_at=DEPARTURE,
        at=DEPARTURE-timedelta(seconds=seconds+offset)) == expected


@pytest.mark.parametrize("offset", [0, 1])
@pytest.mark.parametrize("role", ["PASSAGEIRO", "MOTORISTA"])
def test_policy_rejects_departure_or_later(role, offset):
    with pytest.raises(api().CancellationRefused) as error:
        api().CancellationPolicy.classify(
            role=role, departure_at=DEPARTURE, at=DEPARTURE+timedelta(seconds=offset))
    assert error.value.code == "departure_reached"


def test_policy_midnight_offsets_and_microseconds():
    service = api().CancellationPolicy
    at = (DEPARTURE-timedelta(hours=2)).astimezone(dt_timezone(timedelta(hours=-3)))
    assert at.day != DEPARTURE.day
    assert service.classify(role="PASSAGEIRO", departure_at=DEPARTURE, at=at) == "TEMPESTIVO"
    assert service.classify(role="PASSAGEIRO", departure_at=DEPARTURE,
                            at=at+timedelta(microseconds=1)) == "TARDIO"


@pytest.mark.parametrize("field,bad", [("at", None), ("at", "2030"), ("at", datetime(2030, 1, 1)),
                                       ("departure_at", None), ("departure_at", datetime(2030, 1, 1))])
def test_policy_rejects_invalid_or_naive_instants(field, bad):
    args = dict(role="PASSAGEIRO", departure_at=DEPARTURE, at=DEPARTURE-timedelta(days=1))
    args[field] = bad
    with pytest.raises(ValidationError):
        api().CancellationPolicy.classify(**args)


def test_policy_rejects_unknown_role():
    with pytest.raises(ValidationError):
        api().CancellationPolicy.classify(role="OUTRO", departure_at=DEPARTURE,
                                          at=DEPARTURE-timedelta(days=1))


@pytest.mark.django_db
@pytest.mark.parametrize("offset,expected", [(1, "TEMPESTIVO"), (0, "TEMPESTIVO"), (-1, "TARDIO")])
def test_booking_cancellation_borders_capture_clock_once_and_audit(cancellation_scene, offset, expected):
    scene = cancellation_scene
    at = scene.departure-timedelta(seconds=7200+offset)
    clock = Mock(return_value=at)
    accounts_before = list(get_user_model().objects.order_by("pk").values())
    booking = api().CancellationService.cancel_booking(
        user=scene.passenger, booking_id=scene.booking.pk, clock=clock)
    clock.assert_called_once_with()
    booking.refresh_from_db()
    assert booking.status == "CANCELADA" and booking.cancelled_at == at
    event = records().objects.get(booking=booking)
    assert event.actor_id == scene.passenger.pk and event.offer_id == scene.offer.pk
    assert event.occurred_at == at and event.classification == expected
    scene.offer.refresh_from_db()
    assert scene.offer.seats == 1
    assert not RideBooking.objects.filter(offer=scene.offer, status="CONFIRMADA").exists()
    assert list(get_user_model().objects.order_by("pk").values()) == accounts_before


@pytest.mark.django_db
@pytest.mark.parametrize("offset", [0, 1])
def test_refusal_preserves_all_state(cancellation_scene, offset):
    scene = cancellation_scene
    before = list(RideBooking.objects.values())
    with pytest.raises(api().CancellationRefused):
        api().CancellationService.cancel_booking(
            user=scene.passenger, booking_id=scene.booking.pk,
            clock=lambda: scene.departure+timedelta(seconds=offset))
    assert list(RideBooking.objects.values()) == before
    assert records().objects.count() == 0
    assert RideOffer.objects.get(pk=scene.offer.pk).seats == 1


@pytest.mark.django_db
@pytest.mark.parametrize("kind", ["other", "driver", "pending", "disabled", "wrong_role", "anonymous"])
def test_only_eligible_owner_cancels(cancellation_scene, kind):
    from django.contrib.auth.models import AnonymousUser
    scene = cancellation_scene
    actor = {"other": scene.other, "driver": scene.driver,
             "anonymous": AnonymousUser()}.get(kind, scene.passenger)
    changes = {"pending": {"academic_status": "PENDENTE"}, "disabled": {"is_active": False},
               "wrong_role": {"role": "MOTORISTA"}}
    if kind in changes:
        get_user_model().objects.filter(pk=actor.pk).update(**changes[kind])
    with pytest.raises(PermissionDenied):
        api().CancellationService.cancel_booking(
            user=actor, booking_id=scene.booking.pk, clock=lambda: scene.departure-timedelta(days=1))
    assert RideBooking.objects.get(pk=scene.booking.pk).status == "CONFIRMADA"
    assert not records().objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("booking_id", [None, True, 0, "1", 999999999])
def test_invalid_booking_id_has_no_effect(cancellation_scene, booking_id):
    with pytest.raises(ValidationError):
        api().CancellationService.cancel_booking(
            user=cancellation_scene.passenger, booking_id=booking_id)
    assert not records().objects.exists()


@pytest.mark.django_db
def test_record_constraints_and_timestamps(cancellation_scene):
    scene = cancellation_scene
    api().CancellationService.cancel_booking(
        user=scene.passenger, booking_id=scene.booking.pk,
        clock=lambda: scene.departure-timedelta(hours=3))
    event = records().objects.get()
    with pytest.raises(IntegrityError), transaction.atomic():
        records().objects.bulk_create([records()(
            actor=scene.passenger, offer=scene.offer, booking=scene.booking,
            occurred_at=event.occurred_at, classification=event.classification)])
    with pytest.raises(IntegrityError), transaction.atomic():
        records().objects.filter(pk=event.pk).update(classification="INVALIDA")
    event.occurred_at = event.occurred_at.replace(tzinfo=None)
    with pytest.raises(ValidationError) as error:
        event.full_clean()
    assert "occurred_at" in error.value.message_dict
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, records()._meta.db_table)
    assert constraints["cancellation_booking_unique"]["unique"]
    assert constraints["cancellation_class_valid"]["check"]


@pytest.mark.django_db
def test_audit_target_matches_offer_and_null_target_is_unique(cancellation_scene):
    scene = cancellation_scene
    other = RideOffer.objects.create(
        driver=scene.driver, origin=scene.points[0], destination=scene.points[-1],
        departure_at=scene.departure+timedelta(days=1), seats=1,
        vehicle_model="Outro Sintético", vehicle_color="Azul", vehicle_plate="FICTICIO")
    event = records()(actor=scene.passenger, offer=other, booking=scene.booking,
                      occurred_at=scene.departure-timedelta(days=1), classification="TEMPESTIVO")
    with pytest.raises(ValidationError) as error:
        event.full_clean()
    assert "offer" in error.value.message_dict
    # Validate the nullable schema reserved for future offer cancellation, not its service.
    values = dict(actor=scene.driver, offer=scene.offer, booking=None,
                  occurred_at=scene.departure-timedelta(days=1), classification="TEMPESTIVO")
    records().objects.create(**values)
    with pytest.raises(IntegrityError), transaction.atomic():
        records().objects.bulk_create([records()(**values)])
    for name in ("actor", "offer", "booking"):
        assert records()._meta.get_field(name).remote_field.on_delete.__name__ == "PROTECT"
    with pytest.raises(IntegrityError), transaction.atomic():
        RideOffer.objects.filter(pk=scene.offer.pk).update(status="INVALIDA")
