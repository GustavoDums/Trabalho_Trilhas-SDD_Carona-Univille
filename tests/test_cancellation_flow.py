"""Feature 005/T003 — parcela de reserva da T025; REQ-006/REQ-007/REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

import pytest
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connection, connections, transaction
from django.core.exceptions import ValidationError
from django.test import Client

from rides.models import RideBooking, RideOffer
from rides.services.booking_service import BookingService, NoSeatsAvailable
from rides.services.matching_service import MatchingService, SearchQuery
from .test_cancellation_deadlines import api, records


def cancel(scene, **overrides):
    args = dict(user=scene.passenger, booking_id=scene.booking.pk,
                clock=lambda: scene.departure-timedelta(hours=3))
    args.update(overrides)
    return api().CancellationService.cancel_booking(**args)


@pytest.mark.django_db
def test_release_is_derived_idempotent_and_repeat_after_departure_does_not_reclassify(cancellation_scene):
    scene = cancellation_scene
    first = cancel(scene)
    event = records().objects.get()
    snapshot = list(RideBooking.objects.values())
    repeated = cancel(scene, clock=lambda: scene.departure+timedelta(days=1))
    assert repeated.pk == first.pk
    assert list(RideBooking.objects.values()) == snapshot
    assert records().objects.get().occurred_at == event.occurred_at
    assert records().objects.count() == 1
    scene.offer.refresh_from_db()
    assert scene.offer.seats == 1
    assert scene.offer.seats-RideBooking.objects.filter(offer=scene.offer, status="CONFIRMADA").count() == 1
    new = BookingService.create_booking(
        passenger=scene.other, offer_id=scene.offer.pk,
        boarding_point_id=scene.points[1].pk, alighting_point_id=scene.points[-1].pk)
    assert new.status == "CONFIRMADA"
    assert RideBooking.objects.filter(offer=scene.offer, status="CONFIRMADA").count() == 1


@pytest.mark.django_db
def test_legacy_cancelled_booking_is_not_given_a_fabricated_event(cancellation_scene):
    scene = cancellation_scene
    # Simulate an existing CANCELADA row created before cancellation audit existed.
    RideBooking.objects.filter(pk=scene.booking.pk).update(status="CANCELADA")
    result = cancel(scene)
    assert result.status == "CANCELADA" and result.cancelled_at is None
    assert not records().objects.exists()


@pytest.mark.django_db
def test_audit_failure_rolls_back_booking_timestamp_and_event(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    model = records()
    original = model.save

    def fail_after_audit_insert(self, *args, **kwargs):
        original(self, *args, **kwargs)
        raise RuntimeError("Falha sintética na auditoria")

    before = list(RideBooking.objects.values())
    with monkeypatch.context() as patch:
        patch.setattr(model, "save", fail_after_audit_insert)
        with pytest.raises(RuntimeError):
            cancel(scene)
    assert list(RideBooking.objects.values()) == before and not model.objects.exists()
    cancel(scene)
    assert model.objects.count() == 1


@pytest.mark.django_db
def test_release_is_immediate_in_search_and_private_details_are_revoked(cancellation_scene):
    scene = cancellation_scene
    q = SearchQuery(boarding_id=scene.points[0].pk, alighting_id=scene.points[-1].pk,
                    desired_at=scene.departure)
    assert MatchingService.search(passenger=scene.other, query=q)[0].available_seats == 0
    client = Client()
    client.force_login(scene.passenger)
    assert scene.offer.vehicle_plate in client.get("/caronas/minhas-reservas/").content.decode()
    cancel(scene)
    assert MatchingService.search(passenger=scene.other, query=q)[0].available_seats == 1
    private = client.get("/caronas/minhas-reservas/")
    assert private.status_code == 200
    assert private.context["bookings"][0].vehicle_plate is None
    assert scene.offer.vehicle_plate not in private.content.decode()


@pytest.mark.django_db
def test_closed_offer_is_rejected_by_existing_services_without_implementing_offer_cancel(cancellation_scene):
    scene = cancellation_scene
    RideOffer.objects.filter(pk=scene.offer.pk).update(status="CANCELADA")
    with pytest.raises(ValidationError):
        BookingService.create_booking(
            passenger=scene.other, offer_id=scene.offer.pk,
            boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk)
    q = SearchQuery(boarding_id=scene.points[0].pk, alighting_id=scene.points[-1].pk,
                    desired_at=scene.departure)
    assert MatchingService.search(passenger=scene.other, query=q) == ()


@pytest.mark.django_db
def test_nullable_times_and_valid_offer_status_are_enforced(cancellation_scene):
    scene = cancellation_scene
    assert scene.offer.status == "ABERTA" and scene.offer.cancelled_at is None
    scene.booking.cancelled_at = scene.departure.replace(tzinfo=None)
    with pytest.raises(ValidationError):
        scene.booking.full_clean()
    scene.offer.cancelled_at = scene.departure.replace(tzinfo=None)
    with pytest.raises(ValidationError):
        scene.offer.full_clean()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("rival", ["reserve", "cancel"])
def test_cancellation_concurrency_preserves_capacity_and_single_event(
        cancellation_scene, rival, record_testsuite_property):
    import json
    scene = cancellation_scene
    assert connection.vendor == "postgresql" and not connection.in_atomic_block
    service = api()
    barrier = Barrier(2, timeout=10)

    def worker(action):
        close_old_connections()
        try:
            try:
                with transaction.atomic():
                    with connections["default"].cursor() as cursor:
                        cursor.execute("SET LOCAL lock_timeout = '10s'")
                        cursor.execute("SELECT pg_backend_pid(), txid_current()")
                        backend, txid = cursor.fetchone()
                    actor = get_user_model().objects.get(
                        pk=scene.other.pk if action == "reserve" else scene.passenger.pk)
                    barrier.wait()
                    if action == "reserve":
                        BookingService.create_booking(
                            passenger=actor, offer_id=scene.offer.pk,
                            boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk)
                        result = "confirmed"
                    else:
                        service.CancellationService.cancel_booking(
                            user=actor, booking_id=scene.booking.pk,
                            clock=lambda: scene.departure-timedelta(hours=3))
                        result = "cancelled"
                return result, backend, txid
            except NoSeatsAvailable:
                return "no_seats", backend, txid
        finally:
            connections["default"].close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker, action) for action in ("cancel", rival)]
        outcomes = [future.result(timeout=20) for future in futures]
    assert len({outcome[1] for outcome in outcomes}) == 2
    assert len({outcome[2] for outcome in outcomes}) == 2
    scene.booking.refresh_from_db()
    scene.offer.refresh_from_db()
    assert scene.booking.status == "CANCELADA"
    assert records().objects.filter(booking=scene.booking).count() == 1
    confirmed = RideBooking.objects.filter(offer=scene.offer, status="CONFIRMADA").count()
    assert scene.offer.seats == 1 and confirmed <= 1
    if rival == "cancel":
        assert [value[0] for value in outcomes] == ["cancelled", "cancelled"]
        assert confirmed == 0
    else:
        assert outcomes[0][0] == "cancelled" and outcomes[1][0] in ("confirmed", "no_seats")
        if outcomes[1][0] == "no_seats":
            assert confirmed == 0
            BookingService.create_booking(
                passenger=scene.other, offer_id=scene.offer.pk,
                boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk)
        assert RideBooking.objects.filter(offer=scene.offer, status="CONFIRMADA").count() == 1
    record_testsuite_property("cancellation_race_"+rival, json.dumps({
        "backend_pids": [item[1] for item in outcomes], "txids": [item[2] for item in outcomes],
        "outcomes": [item[0] for item in outcomes], "confirmed_before_retry": confirmed,
        "capacity": scene.offer.seats, "audit_records": records().objects.count()}))
