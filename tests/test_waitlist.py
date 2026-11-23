"""Feature 011/T001, roadmap T039, REQ-013 e REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from importlib import import_module
from threading import Barrier

import pytest
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, connections, transaction
from django.test import Client

from notifications.services import NotificationService
from rides.models import RideBooking, RideOffer, Waypoint
from rides.services.booking_service import BookingService
from rides.services.cancellation_service import CancellationService

pytestmark = pytest.mark.django_db


@pytest.fixture
def scene(cancellation_scene, academic_user_factory):
    scene = cancellation_scene
    scene.next_passenger = academic_user_factory(password=None)
    scene.next_passenger.academic_status = "ATIVA"
    scene.next_passenger.save(update_fields=["academic_status"])
    return scene


def service():
    return import_module("rides.services.waitlist_service").WaitlistService


def points(scene):
    return {"boarding_point_id": scene.points[0].pk, "alighting_point_id": scene.points[2].pk}


def join(scene, passenger, **overrides):
    return service().join(passenger=passenger, offer_id=scene.offer.pk, **(points(scene) | overrides))


def release(scene, booking):
    # Libera capacidade para exercitar o serviço isolado do gatilho da T040.
    RideBooking.objects.filter(pk=booking.pk).update(
        status=RideBooking.Status.CANCELADA, cancelled_at=scene.departure - timedelta(hours=8),
    )


def entries():
    return apps.get_model("rides", "WaitlistEntry").objects


def test_fifo_promotes_one_per_seat_and_keeps_original_segment(scene):
    first = join(scene, scene.other, boarding_point_id=scene.points[1].pk)
    second = join(scene, scene.next_passenger)
    repeated = join(scene, scene.other)
    assert repeated.pk == first.pk
    assert repeated.boarding_point_id == scene.points[1].pk
    assert list(entries().filter(offer=scene.offer)) == [first, second]
    assert service().promote_next(offer_id=scene.offer.pk) is None

    release(scene, scene.booking)
    promoted = service().promote_next(offer_id=scene.offer.pk)

    assert promoted.passenger_id == scene.other.pk
    assert promoted.boarding_point_id == scene.points[1].pk
    assert promoted.status == RideBooking.Status.CONFIRMADA
    assert list(entries().filter(offer=scene.offer)) == [second]
    assert service().promote_next(offer_id=scene.offer.pk) is None
    release(scene, promoted)
    assert service().promote_next(offer_id=scene.offer.pk).passenger_id == scene.next_passenger.pk
    assert not entries().filter(offer=scene.offer).exists()


def test_fifo_skips_a_passenger_who_became_ineligible(scene):
    join(scene, scene.other)
    join(scene, scene.next_passenger)
    scene.other.is_active = False
    scene.other.save(update_fields=["is_active"])
    release(scene, scene.booking)

    assert service().promote_next(offer_id=scene.offer.pk).passenger_id == scene.next_passenger.pk
    assert not entries().filter(offer=scene.offer).exists()


def test_fifo_preserves_the_queue_when_the_driver_is_unavailable(scene):
    entry = join(scene, scene.other)
    release(scene, scene.booking)
    scene.driver.is_active = False
    scene.driver.save(update_fields=["is_active"])

    assert service().promote_next(offer_id=scene.offer.pk) is None
    assert entries().filter(pk=entry.pk).exists()


def test_fifo_skips_a_passenger_with_an_existing_booking(scene):
    join(scene, scene.other)
    join(scene, scene.next_passenger)
    RideOffer.objects.filter(pk=scene.offer.pk).update(seats=3)
    BookingService.create_booking(passenger=scene.other, offer_id=scene.offer.pk, **points(scene))

    assert service().promote_next(offer_id=scene.offer.pk).passenger_id == scene.next_passenger.pk
    assert not entries().filter(offer=scene.offer).exists()


def test_fifo_revalidates_the_queued_segment_against_current_route(scene):
    join(scene, scene.other, boarding_point_id=scene.points[1].pk)
    join(scene, scene.next_passenger)
    Waypoint.objects.filter(offer=scene.offer, point=scene.points[1]).delete()
    release(scene, scene.booking)

    assert service().promote_next(offer_id=scene.offer.pk).passenger_id == scene.next_passenger.pk
    assert not entries().filter(offer=scene.offer).exists()


def test_fifo_rolls_back_reservation_and_queue_removal_on_unexpected_failure(scene, monkeypatch):
    skipped = join(scene, scene.other)
    entry = join(scene, scene.next_passenger)
    scene.other.academic_status = "PENDENTE"
    scene.other.save(update_fields=["academic_status"])
    release(scene, scene.booking)

    def fail(_booking):
        raise RuntimeError("falha sintética na notificação")

    monkeypatch.setattr(NotificationService, "booking_confirmed", fail)
    with pytest.raises(RuntimeError, match="falha sintética"):
        service().promote_next(offer_id=scene.offer.pk)

    assert list(entries().filter(offer=scene.offer)) == [skipped, entry]
    assert not RideBooking.objects.filter(offer=scene.offer, status="CONFIRMADA").exists()


@pytest.mark.django_db(transaction=True)
def test_fifo_concurrent_promotions_assign_only_one_booking(scene):
    assert connection.vendor == "postgresql"
    join(scene, scene.other)
    second = join(scene, scene.next_passenger)
    release(scene, scene.booking)
    ready = Barrier(2, timeout=10)

    def promote():
        try:
            ready.wait()
            return service().promote_next(offer_id=scene.offer.pk)
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as threads:
        results = list(threads.map(lambda _: promote(), range(2), timeout=20))

    assert [result.passenger_id for result in results if result] == [scene.other.pk]
    assert list(entries().filter(offer=scene.offer)) == [second]
    assert RideBooking.objects.filter(offer=scene.offer, status="CONFIRMADA").count() == 1


def test_join_rejects_confirmed_passenger_invalid_segment_or_available_seat(scene):
    with pytest.raises(ValidationError, match="reserva confirmada"):
        join(scene, scene.passenger)
    with pytest.raises(ValidationError):
        join(scene, scene.other, boarding_point_id=scene.points[-1].pk)
    release(scene, scene.booking)
    with pytest.raises(ValidationError, match="vaga"):
        join(scene, scene.other)
    assert not entries().filter(offer=scene.offer).exists()


def test_waitlist_constraints_protect_against_direct_duplicate_and_equal_points(scene):
    entry = join(scene, scene.other)
    with pytest.raises(IntegrityError), transaction.atomic():
        entries().create(offer=scene.offer, passenger=scene.other, **points(scene))
    with pytest.raises(IntegrityError), transaction.atomic():
        entries().create(
            offer=scene.offer, passenger=scene.next_passenger,
            boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[0].pk,
        )
    assert list(entries().filter(offer=scene.offer)) == [entry]


def test_fifo_preserves_entries_for_closed_offer_and_returns_none_for_empty_queue(scene):
    release(scene, scene.booking)
    assert service().promote_next(offer_id=scene.offer.pk) is None
    promoted_by_other_path = RideBooking.objects.create(
        offer=scene.offer, passenger=scene.passenger, **points(scene),
    )
    entry = join(scene, scene.other)
    release(scene, promoted_by_other_path)
    CancellationService.cancel_offer(
        user=scene.driver, offer_id=scene.offer.pk,
        clock=lambda: scene.departure - timedelta(hours=8),
    )
    assert service().promote_next(offer_id=scene.offer.pk) is None
    assert entries().filter(pk=entry.pk).exists()


def test_join_uses_session_csrf_and_the_segment_from_search(scene):
    url = f"/caronas/{scene.offer.pk}/fila/"
    data = points(scene) | {"passenger_id": scene.next_passenger.pk}
    client = Client(enforce_csrf_checks=True)
    assert client.post(url, data).status_code == 302
    client.force_login(scene.driver)
    assert client.get(url).status_code == 403
    client.force_login(scene.other)
    assert client.get(url).status_code == 405
    assert client.post(url, data).status_code == 403

    page = client.get("/caronas/buscar/", {
        "boarding_id": scene.points[0].pk, "alighting_id": scene.points[-1].pk,
        "desired_at": scene.departure.isoformat(),
    })
    assert f'action="{url}"' in page.content.decode()
    token = client.cookies["csrftoken"].value
    assert client.post(url, data | {"csrfmiddlewaretoken": token})["Location"] == "/caronas/minhas-reservas/"
    entry = entries().get(offer=scene.offer)
    assert (entry.passenger_id, entry.boarding_point_id, entry.alighting_point_id) == (
        scene.other.pk, scene.points[0].pk, scene.points[-1].pk,
    )
    assert client.post(url, {"csrfmiddlewaretoken": token}).status_code == 400
    assert entries().filter(offer=scene.offer).count() == 1
