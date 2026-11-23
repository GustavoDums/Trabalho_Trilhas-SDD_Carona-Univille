"""Feature 004/T002 local — roadmap T020; REQ-006, REQ-002, REQ-017."""
from datetime import timedelta
from itertools import product
from types import SimpleNamespace

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from rides.models import RideOffer, RoutePoint, Waypoint

pytestmark = pytest.mark.django_db


def booking_model():
    return apps.get_model("rides", "RideBooking")


@pytest.fixture
def booking_scene(academic_user_factory):
    driver = academic_user_factory(role="MOTORISTA", password=None)
    passenger = academic_user_factory(password=None)
    for user in (driver, passenger):
        user.academic_status = "ATIVA"
        user.save(update_fields=["academic_status", "updated_at"])
    catalog = {point.code: point for point in RoutePoint.objects.all()}
    points = [catalog[code] for code in
              ("terminal-norte", "campus-univille", "bairro-america", "terminal-central")]
    offer = RideOffer.objects.create(
        driver=driver, origin=points[0], destination=points[3],
        departure_at=timezone.now()+timedelta(days=1), seats=3,
        vehicle_model="Veículo Sintético", vehicle_color="Azul", vehicle_plate="FICTICIO")
    Waypoint.objects.create(offer=offer, point=points[2], position=2)
    Waypoint.objects.create(offer=offer, point=points[1], position=1)
    return SimpleNamespace(driver=driver, passenger=passenger, offer=offer, points=points)


def new_booking(scene, **overrides):
    values = dict(offer=scene.offer, passenger=scene.passenger,
                  boarding_point=scene.points[0], alighting_point=scene.points[3])
    values.update(overrides)
    return booking_model()(**values)


def test_booking_fields_and_protection():
    model = booking_model()
    assert connection.vendor == "postgresql"
    assert model.Status.CONFIRMADA == "CONFIRMADA"
    assert model.Status.CANCELADA == "CANCELADA"
    assert set(model.Status.values) == {"CONFIRMADA", "CANCELADA"}
    assert model._meta.get_field("status").max_length == 10
    assert model._meta.get_field("status").default == "CONFIRMADA"
    for name in ("offer", "passenger", "boarding_point", "alighting_point"):
        field = model._meta.get_field(name)
        assert not field.null and field.remote_field.on_delete.__name__ == "PROTECT"
    assert set(field.name for field in model._meta.fields) == {
        "id", "offer", "passenger", "boarding_point", "alighting_point", "status",
        "created_at", "updated_at"}


def test_booking_default_and_no_side_effect_on_capacity(booking_scene):
    before = (list(RideOffer.objects.values()), list(RoutePoint.objects.values()),
              list(Waypoint.objects.values()), list(get_user_model().objects.values()))
    booking = new_booking(booking_scene)
    booking.save()
    booking.refresh_from_db()
    assert booking.status == "CONFIRMADA"
    assert booking.offer == booking_scene.offer and booking.passenger == booking_scene.passenger
    assert timezone.is_aware(booking.created_at) and timezone.is_aware(booking.updated_at)
    assert booking_scene.offer.bookings.get() == booking
    assert booking_scene.passenger.ride_bookings.get() == booking
    assert (list(RideOffer.objects.values()), list(RoutePoint.objects.values()),
            list(Waypoint.objects.values()), list(get_user_model().objects.values())) == before


def test_booking_update_timestamp_and_cancelled_history(booking_scene, monkeypatch):
    booking = new_booking(booking_scene)
    booking.save()
    created = booking.created_at
    later = booking.updated_at + timedelta(seconds=1)
    monkeypatch.setattr(timezone, "now", lambda: later)
    get_user_model().objects.filter(pk=booking_scene.passenger.pk).update(academic_status="PENDENTE")
    booking.status = "CANCELADA"
    booking.save()
    booking.refresh_from_db()
    assert booking.created_at == created and booking.updated_at == later
    assert booking.status == "CANCELADA"


def test_booking_rejects_self_even_if_driver_role_was_changed(booking_scene):
    # Cross-table author check must remain independent of the account role check.
    get_user_model().objects.filter(pk=booking_scene.driver.pk).update(role="PASSAGEIRO")
    booking = new_booking(booking_scene, passenger=booking_scene.driver)
    with pytest.raises(ValidationError) as error:
        booking.save()
    assert "passenger" in error.value.message_dict
    assert any("própria" in message for message in error.value.message_dict["passenger"])
    assert not booking_model().objects.exists()


@pytest.mark.parametrize("changes", [
    {"academic_status": "PENDENTE"}, {"is_active": False}, {"role": "MOTORISTA"},
])
def test_booking_new_passenger_must_be_eligible(booking_scene, changes):
    get_user_model().objects.filter(pk=booking_scene.passenger.pk).update(**changes)
    with pytest.raises(ValidationError) as error:
        new_booking(booking_scene).save()
    assert "passenger" in error.value.message_dict
    assert not booking_model().objects.exists()


@pytest.mark.parametrize("boarding,alighting", list(product(range(4), repeat=2)))
def test_booking_all_itinerary_pairs(booking_scene, boarding, alighting):
    booking = new_booking(
        booking_scene, boarding_point=booking_scene.points[boarding],
        alighting_point=booking_scene.points[alighting])
    if boarding < alighting:
        booking.save()
        assert booking.pk
    else:
        with pytest.raises(ValidationError) as error:
            booking.save()
        assert "alighting_point" in error.value.message_dict
        assert not booking_model().objects.exists()


@pytest.mark.parametrize("field", ["boarding_point", "alighting_point"])
def test_booking_point_outside_offer(booking_scene, field):
    outsider = RoutePoint.objects.create(code="ponto-fora", name="Ponto Sintético Externo")
    with pytest.raises(ValidationError) as error:
        new_booking(booking_scene, **{field: outsider}).save()
    assert field in error.value.message_dict


def test_booking_direct_route_and_ambiguous_legacy_data(booking_scene):
    booking_scene.offer.waypoints.all().delete()
    booking = new_booking(booking_scene)
    booking.save()
    # Historical malformed itinerary, bypassing Python clean but not SQL constraints.
    Waypoint.objects.bulk_create([
        Waypoint(offer=booking_scene.offer, point=booking_scene.points[0], position=1)])
    with pytest.raises(ValidationError):
        booking.full_clean()


@pytest.mark.parametrize("field", ["offer", "passenger", "boarding_point", "alighting_point"])
def test_booking_required_relations(booking_scene, field):
    with pytest.raises(ValidationError) as error:
        new_booking(booking_scene, **{field: None}).save()
    assert field in error.value.message_dict


@pytest.mark.parametrize("field", ["offer_id", "passenger_id", "boarding_point_id", "alighting_point_id"])
def test_booking_invalid_foreign_keys_are_validation_errors(booking_scene, field):
    booking = new_booking(booking_scene)
    setattr(booking, field, 999999999)
    with pytest.raises(ValidationError):
        booking.save()


@pytest.mark.parametrize("status", ["", "PENDENTE", "confirmada", "X" * 11])
def test_booking_invalid_status_in_model(booking_scene, status):
    with pytest.raises(ValidationError) as error:
        new_booking(booking_scene, status=status).save()
    assert "status" in error.value.message_dict


def test_booking_active_uniqueness_in_model(booking_scene):
    new_booking(booking_scene).save()
    with pytest.raises(ValidationError):
        new_booking(booking_scene, boarding_point=booking_scene.points[1]).save()
    assert booking_model().objects.count() == 1


def test_booking_active_uniqueness_in_postgresql(booking_scene):
    new_booking(booking_scene).save()
    with pytest.raises(IntegrityError), transaction.atomic():
        booking_model().objects.bulk_create([new_booking(booking_scene)])
    assert booking_model().objects.count() == 1


@pytest.mark.parametrize("bad", ["status", "points"])
def test_booking_sql_checks_cannot_be_bypassed(booking_scene, bad):
    booking = new_booking(booking_scene)
    booking.save()
    values = {"status": "PENDENTE"} if bad == "status" else {
        "alighting_point_id": booking.boarding_point_id}
    with pytest.raises(IntegrityError), transaction.atomic():
        booking_model().objects.filter(pk=booking.pk).update(**values)
    booking.refresh_from_db()
    assert booking.status == "CONFIRMADA"
    assert booking.boarding_point_id != booking.alighting_point_id


def test_booking_cancelled_records_allow_new_active_without_erasing_history(booking_scene):
    for _ in range(2):
        new_booking(booking_scene, status="CANCELADA").save()
    active = new_booking(booking_scene)
    active.save()
    assert booking_model().objects.count() == 3
    assert booking_model().objects.filter(status="CONFIRMADA").count() == 1
    booking_scene.offer.refresh_from_db()
    assert booking_scene.offer.seats == 3


def test_booking_other_passenger_or_offer_is_not_a_duplicate(booking_scene, academic_user_factory):
    new_booking(booking_scene).save()
    passenger = academic_user_factory(password=None)
    passenger.academic_status = "ATIVA"
    passenger.save(update_fields=["academic_status", "updated_at"])
    new_booking(booking_scene, passenger=passenger).save()
    other = RideOffer.objects.create(
        driver=booking_scene.driver, origin=booking_scene.points[0], destination=booking_scene.points[3],
        departure_at=timezone.now()+timedelta(days=2), seats=3,
        vehicle_model="Outro Sintético", vehicle_color="Verde", vehicle_plate="FICTICIO")
    new_booking(booking_scene, offer=other).save()
    assert booking_model().objects.count() == 3


@pytest.mark.parametrize("target", ["offer", "passenger", "boarding_point", "alighting_point"])
def test_booking_historical_relations_are_protected(booking_scene, target):
    booking = new_booking(booking_scene, status="CANCELADA")
    booking.save()
    with pytest.raises(ProtectedError):
        getattr(booking, target).delete()
    assert booking_model().objects.filter(pk=booking.pk).exists()


def test_booking_migration_schema_on_postgresql():
    model = booking_model()
    from django.db.migrations.recorder import MigrationRecorder
    assert MigrationRecorder(connection).migration_qs.filter(
        app="rides", name="0003_ridebooking").exists()
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, model._meta.db_table)
    assert constraints["booking_active_passenger_unique"]["unique"]
    assert constraints["booking_status_valid"]["check"]
    assert constraints["booking_points_distinct"]["check"]
    assert all(any(info.get("foreign_key") for info in constraints.values()
                   if name in info["columns"])
               for name in ("offer_id", "passenger_id", "boarding_point_id", "alighting_point_id"))
