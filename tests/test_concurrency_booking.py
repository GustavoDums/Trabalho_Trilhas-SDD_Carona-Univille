"""Feature 004/T003 local — núcleo da T021, REQ-006/REQ-017; PostgreSQL real."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone as dt_timezone
from importlib import import_module
from threading import Barrier
from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, close_old_connections, connection, connections, transaction
from django.utils import timezone

from rides.models import RideBooking, RideOffer, RoutePoint, Waypoint

NOW = datetime(2030, 1, 2, 12, tzinfo=dt_timezone.utc)


def api():
    return import_module("rides.services.booking_service")


@pytest.fixture
def service_scene(academic_user_factory, monkeypatch):
    monkeypatch.setattr(timezone, "now", lambda: NOW)
    driver = academic_user_factory(role="MOTORISTA", password=None)
    first = academic_user_factory(password=None)
    second = academic_user_factory(password=None)
    for user in (driver, first, second):
        user.academic_status = "ATIVA"
        user.save(update_fields=["academic_status", "updated_at"])
    points = [RoutePoint.objects.get_or_create(code=code, defaults={"name": name})[0]
              for code, name in (
                  ("reserve-origin", "Origem Sintética"), ("reserve-stop", "Parada Sintética"),
                  ("reserve-destination", "Destino Sintético"))]
    offer = RideOffer.objects.create(
        driver=driver, origin=points[0], destination=points[2],
        departure_at=NOW+timedelta(days=1), seats=1,
        vehicle_model="Veículo Sintético", vehicle_color="Azul", vehicle_plate="FICTICIO")
    Waypoint.objects.create(offer=offer, point=points[1], position=1)
    return SimpleNamespace(driver=driver, first=first, second=second, offer=offer, points=points)


def reserve(scene, **overrides):
    args = dict(passenger=scene.first, offer_id=scene.offer.pk,
                boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[2].pk)
    args.update(overrides)
    return api().BookingService.create_booking(**args)


@pytest.mark.django_db
def test_service_confirms_once_and_preserves_capacity(service_scene):
    booking = reserve(service_scene)
    assert isinstance(booking, RideBooking) and booking.status == "CONFIRMADA"
    assert booking.boarding_point_id == service_scene.points[0].pk
    assert booking.alighting_point_id == service_scene.points[2].pk
    service_scene.offer.refresh_from_db()
    assert service_scene.offer.seats == 1
    with pytest.raises(api().NoSeatsAvailable) as error:
        reserve(service_scene, passenger=service_scene.second, boarding_point_id=service_scene.points[1].pk)
    assert error.value.code == "no_seats"
    assert RideBooking.objects.filter(status="CONFIRMADA").count() == 1


@pytest.mark.django_db
def test_service_duplicate_is_rejected_before_capacity_error(service_scene):
    reserve(service_scene)
    with pytest.raises(ValidationError) as error:
        reserve(service_scene)
    assert error.value.code == "already_booked"
    assert RideBooking.objects.count() == 1


@pytest.mark.django_db
def test_service_cancelled_history_does_not_consume_seat(service_scene):
    RideBooking.objects.create(
        offer=service_scene.offer, passenger=service_scene.first,
        boarding_point=service_scene.points[0], alighting_point=service_scene.points[2],
        status="CANCELADA")
    assert reserve(service_scene).status == "CONFIRMADA"
    assert RideBooking.objects.count() == 2


@pytest.mark.parametrize("subject", ["first", "driver"])
@pytest.mark.parametrize("changes", [
    {"academic_status": "PENDENTE"}, {"is_active": False}, {"role": "OUTRO"},
])
@pytest.mark.django_db
def test_service_revalidates_accounts_not_stale_objects(service_scene, subject, changes):
    get_user_model().objects.filter(pk=getattr(service_scene, subject).pk).update(**changes)
    expected = PermissionDenied if subject == "first" else ValidationError
    with pytest.raises(expected):
        reserve(service_scene)
    assert not RideBooking.objects.exists()


@pytest.mark.django_db
def test_service_self_anonymous_and_deleted_actor_rejected(service_scene):
    from django.contrib.auth.models import AnonymousUser
    with pytest.raises(PermissionDenied):
        reserve(service_scene, passenger=service_scene.driver)
    with pytest.raises(PermissionDenied):
        reserve(service_scene, passenger=AnonymousUser())
    stale = service_scene.first
    get_user_model().objects.filter(pk=stale.pk).delete()
    with pytest.raises(PermissionDenied):
        reserve(service_scene, passenger=stale)
    assert not RideBooking.objects.exists()


@pytest.mark.parametrize("seconds", [-1, 0])
@pytest.mark.django_db
def test_service_rejects_past_and_exact_now(service_scene, seconds):
    RideOffer.objects.filter(pk=service_scene.offer.pk).update(
        departure_at=NOW+timedelta(seconds=seconds))
    with pytest.raises(ValidationError):
        reserve(service_scene)
    assert not RideBooking.objects.exists()


@pytest.mark.parametrize("field", ["offer_id", "boarding_point_id", "alighting_point_id"])
@pytest.mark.parametrize("value", [True, 0, "1", None])
@pytest.mark.django_db
def test_service_validates_id_types(service_scene, field, value):
    with pytest.raises(ValidationError) as error:
        reserve(service_scene, **{field: value})
    assert field in error.value.message_dict
    assert not RideBooking.objects.exists()


@pytest.mark.parametrize("field", ["offer_id", "boarding_point_id", "alighting_point_id"])
@pytest.mark.django_db
def test_service_nonexistent_ids_rejected_without_writes(service_scene, field):
    with pytest.raises(ValidationError):
        reserve(service_scene, **{field: 999999999})
    assert not RideBooking.objects.exists()


@pytest.mark.django_db
def test_service_route_revalidated_and_invalid_route_does_not_fill_offer(service_scene):
    with pytest.raises(ValidationError):
        reserve(service_scene, boarding_point_id=service_scene.points[2].pk)
    assert not RideBooking.objects.exists()
    assert reserve(service_scene).pk


@pytest.mark.django_db
def test_service_rolls_back_failure_after_insert_and_connection_stays_usable(service_scene, monkeypatch):
    original = RideBooking.save

    def fail_after_insert(self, *args, **kwargs):
        original(self, *args, **kwargs)
        raise RuntimeError("Falha sintética após insert")

    with monkeypatch.context() as patch:
        patch.setattr(RideBooking, "save", fail_after_insert)
        with pytest.raises(RuntimeError, match="sintética"):
            reserve(service_scene)
    assert not RideBooking.objects.exists()
    service_scene.offer.refresh_from_db()
    assert service_scene.offer.seats == 1
    assert reserve(service_scene).status == "CONFIRMADA"


@pytest.mark.parametrize("kind", ["duplicate", "other_constraint"])
@pytest.mark.django_db
def test_service_sql_errors_roll_back_savepoint_before_translation(service_scene, monkeypatch, kind):
    original = RideBooking.save

    def sql_failure(self, *args, **kwargs):
        original(self, *args, **kwargs)
        # Inject actual PostgreSQL errors after insert, not mocks of transaction/locks.
        with connection.cursor() as cursor:
            if kind == "duplicate":
                cursor.execute(
                    "INSERT INTO rides_ridebooking "
                    "(status, created_at, updated_at, offer_id, passenger_id, boarding_point_id, alighting_point_id) "
                    "SELECT status, created_at, updated_at, offer_id, passenger_id, boarding_point_id, alighting_point_id "
                    "FROM rides_ridebooking WHERE id = %s", [self.pk])
            else:
                cursor.execute("UPDATE rides_ridebooking SET status = 'INVALIDA' WHERE id = %s", [self.pk])

    with monkeypatch.context() as patch:
        patch.setattr(RideBooking, "save", sql_failure)
        expected = ValidationError if kind == "duplicate" else IntegrityError
        with pytest.raises(expected) as error:
            reserve(service_scene)
        if kind == "duplicate":
            assert error.value.code == "already_booked"
    assert not RideBooking.objects.exists()
    assert reserve(service_scene).status == "CONFIRMADA"


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("same_passenger", [False, True])
def test_concurrent_last_seat_independent_postgresql_transactions(service_scene, same_passenger, record_testsuite_property):
    assert connection.vendor == "postgresql"
    assert not connection.in_atomic_block
    service = api()  # Missing service must fail before opening worker threads in the red phase.
    barrier = Barrier(2, timeout=10)
    actors = [service_scene.first.pk, service_scene.first.pk if same_passenger else service_scene.second.pk]

    def attempt(actor_id):
        close_old_connections()
        try:
            try:
                with transaction.atomic():
                    with connections["default"].cursor() as cursor:
                        cursor.execute("SET LOCAL lock_timeout = '10s'")
                        cursor.execute("SELECT pg_backend_pid(), txid_current()")
                        backend, txid = cursor.fetchone()
                    actor = get_user_model().objects.get(pk=actor_id)
                    barrier.wait()  # Before any service lock, so no barrier-induced deadlock.
                    booking = service.BookingService.create_booking(
                        passenger=actor, offer_id=service_scene.offer.pk,
                        boarding_point_id=service_scene.points[0].pk,
                        alighting_point_id=service_scene.points[2].pk)
                return ("confirmed", backend, txid, booking.pk)
            except ValidationError as error:
                return (error.code, backend, txid, None)
        finally:
            connections["default"].close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(attempt, actor_id) for actor_id in actors]
        outcomes = [future.result(timeout=20) for future in futures]
    expected_error = "already_booked" if same_passenger else "no_seats"
    assert sorted(outcome[0] for outcome in outcomes) == sorted(["confirmed", expected_error])
    assert len({outcome[1] for outcome in outcomes}) == 2
    assert len({outcome[2] for outcome in outcomes}) == 2
    confirmed = RideBooking.objects.filter(offer=service_scene.offer, status="CONFIRMADA").count()
    service_scene.offer.refresh_from_db()
    assert confirmed == 1 and service_scene.offer.seats - confirmed == 0
    assert RideBooking.objects.count() == 1
    assert service_scene.offer.seats == 1
    import json
    record_testsuite_property(
        "last_seat_same_passenger" if same_passenger else "last_seat_two_passengers",
        json.dumps({"backend_pids": [item[1] for item in outcomes],
                    "transaction_ids": [item[2] for item in outcomes],
                    "outcomes": sorted(item[0] for item in outcomes),
                    "confirmed": confirmed, "balance": service_scene.offer.seats-confirmed}),
    )
