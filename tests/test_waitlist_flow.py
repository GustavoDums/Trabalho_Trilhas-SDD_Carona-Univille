"""Feature 011/T002, roadmap T040, REQ-007/013/017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

import pytest
from django.db import connection, connections

from notifications.models import Notification
from notifications.services import NotificationService
from reviews.models import PenaltyRecord
from rides.models import CancellationRecord, RideBooking, RideOffer, WaitlistEntry
from rides.services.booking_service import BookingService
from rides.services.cancellation_service import CancellationService
from rides.services.waitlist_service import WaitlistService

pytestmark = pytest.mark.django_db
PANEL = "/caronas/minhas-reservas/"


@pytest.fixture
def next_passenger(academic_user_factory):
    user = academic_user_factory(password=None, full_name="Terceiro Sintético")
    user.academic_status = "ATIVA"
    user.save(update_fields=["academic_status"])
    return user


def segment(scene):
    return {"boarding_point_id": scene.points[0].pk, "alighting_point_id": scene.points[-1].pk}


def join(scene, user):
    return WaitlistService.join(passenger=user, offer_id=scene.offer.pk, **segment(scene))


def cancel(scene, booking):
    return CancellationService.cancel_booking(
        user=booking.passenger, booking_id=booking.pk,
        clock=lambda: scene.departure - timedelta(hours=1),
    )


def test_http_cancellation_promotes_fifo_updates_private_position_and_notifies(cancellation_scene, next_passenger, client):
    scene = cancellation_scene
    client.force_login(scene.other)
    assert client.post(f"/caronas/{scene.offer.pk}/fila/", segment(scene)).status_code == 302
    second = join(scene, next_passenger)
    assert "Posição na fila: 1" in client.get(PANEL).content.decode()
    client.force_login(next_passenger)
    body = client.get(PANEL, {"passenger_id": scene.other.pk}).content.decode()
    assert "Posição na fila: 2" in body
    assert "Posição na fila: 1" not in body
    assert scene.other.email not in body
    assert scene.offer.vehicle_plate not in body
    client.force_login(scene.driver)
    assert "Posição na fila:" not in client.get(PANEL).content.decode()

    client.force_login(scene.passenger)
    path = f"/caronas/reservas/{scene.booking.pk}/cancelar/"
    assert client.post(path).status_code == 302
    assert client.post(path).status_code == 302

    promoted = RideBooking.objects.get(offer=scene.offer, status="CONFIRMADA")
    assert promoted.passenger_id == scene.other.pk
    assert list(WaitlistEntry.objects.filter(offer=scene.offer)) == [second]
    assert CancellationRecord.objects.filter(booking=scene.booking).count() == 1
    assert set(Notification.objects.filter(booking=promoted).values_list("recipient_id", "kind")) == {
        (scene.other.pk, Notification.Kind.BOOKING_CONFIRMED),
        (scene.driver.pk, Notification.Kind.BOOKING_CONFIRMED),
    }
    client.force_login(scene.other)
    assert "Posição na fila:" not in client.get(PANEL).content.decode()
    assert "Reserva confirmada" in client.get("/notificacoes/").content.decode()
    client.force_login(next_passenger)
    assert "Posição na fila: 1" in client.get(PANEL).content.decode()
    assert "Você ainda não recebeu notificações." in client.get("/notificacoes/").content.decode()


def test_failed_promotion_rolls_back_cancellation_audit_notices_and_queue(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    entry = join(scene, scene.other)
    before = list(Notification.objects.values_list("pk", flat=True))

    def fail(_booking):
        raise RuntimeError("falha sintética no repasse")

    monkeypatch.setattr(NotificationService, "booking_confirmed", fail)
    with pytest.raises(RuntimeError, match="falha sintética"):
        cancel(scene, scene.booking)

    scene.booking.refresh_from_db()
    assert scene.booking.status == "CONFIRMADA"
    assert scene.booking.cancelled_at is None
    assert WaitlistEntry.objects.filter(pk=entry.pk).exists()
    assert not CancellationRecord.objects.filter(booking=scene.booking).exists()
    assert not PenaltyRecord.objects.filter(booking=scene.booking).exists()
    assert list(Notification.objects.values_list("pk", flat=True)) == before


def test_cancelled_offer_does_not_promote_or_display_waitlist(cancellation_scene, client):
    scene = cancellation_scene
    join(scene, scene.other)
    CancellationService.cancel_offer(
        user=scene.driver, offer_id=scene.offer.pk,
        clock=lambda: scene.departure - timedelta(hours=5),
    )
    assert not RideBooking.objects.filter(offer=scene.offer, status="CONFIRMADA").exists()
    assert not Notification.objects.filter(recipient=scene.other).exists()
    client.force_login(scene.other)
    assert "Posição na fila:" not in client.get(PANEL).content.decode()


@pytest.mark.django_db(transaction=True)
def test_concurrent_cancellations_with_crossed_queues_promote_without_deadlock(
    cancellation_scene, academic_user_factory,
):
    scene = cancellation_scene
    other_driver = academic_user_factory(role="MOTORISTA", password=None)
    other_driver.academic_status = "ATIVA"
    other_driver.save(update_fields=["academic_status"])
    other_offer = RideOffer.objects.create(
        driver=other_driver, origin=scene.points[0], destination=scene.points[-1],
        departure_at=scene.departure, seats=1, vehicle_model="Sintético",
        vehicle_color="Azul", vehicle_plate="FICTICIA",
    )
    other_booking = BookingService.create_booking(
        passenger=scene.other, offer_id=other_offer.pk, **segment(scene),
    )
    join(scene, scene.other)
    WaitlistService.join(passenger=scene.passenger, offer_id=other_offer.pk, **segment(scene))
    ready = Barrier(2, timeout=10)

    def cancel_concurrently(booking):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET lock_timeout = '5s'")
            ready.wait()
            return cancel(scene, booking).status
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as threads:
        assert list(threads.map(cancel_concurrently, (scene.booking, other_booking), timeout=20)) == [
            "CANCELADA", "CANCELADA",
        ]

    assert set(RideBooking.objects.filter(status="CONFIRMADA").values_list("offer_id", "passenger_id")) == {
        (scene.offer.pk, scene.other.pk), (other_offer.pk, scene.passenger.pk),
    }
    assert not WaitlistEntry.objects.exists()
