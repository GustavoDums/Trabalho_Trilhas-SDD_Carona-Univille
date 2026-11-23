"""Feature 010/T001 (roadmap T037), REQ-012, REQ-003 e REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from importlib import import_module
from threading import Barrier, Event
from types import SimpleNamespace

import pytest
from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection, connections, transaction
from django.db.models.deletion import ProtectedError

from reviews.models import PenaltyRecord
from rides.models import CancellationRecord, RideBooking, RideOffer, RoutePoint
from rides.services.booking_service import BookingService, NoSeatsAvailable
from rides.services.cancellation_service import CancellationRefused, CancellationService

pytestmark = pytest.mark.django_db


@pytest.fixture
def scene(academic_user_factory):
    passengers = [academic_user_factory(password=None) for _ in range(3)]
    driver = academic_user_factory(role='MOTORISTA', password=None)
    for user in [driver, *passengers]:
        user.academic_status = 'ATIVA'
        user.save(update_fields=['academic_status'])
    origin, destination = [
        RoutePoint.objects.create(code=f'notice-{name}', name=f'{name} sintética')
        for name in ('origem', 'destino')
    ]
    departure = datetime(2030, 1, 4, 12, tzinfo=timezone.utc)
    offer = RideOffer.objects.create(
        driver=driver, origin=origin, destination=destination, departure_at=departure,
        seats=3, vehicle_model='Sintético', vehicle_color='Azul', vehicle_plate='PRIVADA937',
    )
    return SimpleNamespace(driver=driver, passengers=passengers, origin=origin,
                           destination=destination, departure=departure, offer=offer)


def notice_model():
    return apps.get_model('notifications', 'Notification')


def notification_service():
    return import_module('notifications.services').NotificationService


def book(scene, passenger, *, offer=None):
    return BookingService.create_booking(
        passenger=passenger, offer_id=scene.offer.pk if offer is None else offer.pk,
        boarding_point_id=scene.origin.pk, alighting_point_id=scene.destination.pk,
    )


def cancel_booking(scene, booking, *, delay_hours=5):
    return CancellationService.cancel_booking(user=booking.passenger, booking_id=booking.pk,
                                              clock=lambda: scene.departure-timedelta(hours=delay_hours))


def test_confirmation_has_two_private_unread_notices_and_replay_keeps_existing_rows(scene):
    passenger = scene.passengers[0]
    booking = book(scene, passenger)
    notices = notice_model().objects.filter(booking=booking)
    assert set(notices.values_list('recipient_id', flat=True)) == {passenger.pk, scene.driver.pk}
    assert notices.count() == 2
    assert set(notices.values_list('kind', flat=True)) == {'BOOKING_CONFIRMED'}
    assert not notices.exclude(read_at=None).exists()
    assert not notices.exclude(cancellation=None).exists()
    seen = scene.departure-timedelta(days=1)
    notices.filter(recipient=passenger).update(read_at=seen)
    before = list(notices.order_by('pk').values())

    notification_service().booking_confirmed(booking)

    assert list(notices.order_by('pk').values()) == before
    assert {'body', 'email', 'vehicle_plate', 'title'}.isdisjoint(before[0])
    with pytest.raises(ProtectedError):
        booking.delete()


@pytest.mark.parametrize('delay_hours', [5, 1])
def test_booking_cancel_notifies_both_participants_once_and_rebooking_is_distinct(scene, delay_hours):
    booking = book(scene, scene.passengers[0])
    cancel_booking(scene, booking, delay_hours=delay_hours)
    cancel_booking(scene, booking, delay_hours=delay_hours)
    event = CancellationRecord.objects.get(booking=booking)
    notices = notice_model().objects.filter(cancellation=event)
    before = list(notices.order_by('pk').values())

    notification_service().cancellation_recorded(event)
    new_booking = book(scene, scene.passengers[0])

    assert list(notices.order_by('pk').values()) == before
    assert set(notices.values_list('recipient_id', 'kind')) == {
        (booking.passenger_id, 'BOOKING_CANCELLED'), (scene.driver.pk, 'BOOKING_CANCELLED'),
    }
    assert new_booking.pk != booking.pk
    assert notice_model().objects.filter(kind='BOOKING_CONFIRMED').count() == 4
    with pytest.raises(ProtectedError):
        event.delete()


@pytest.mark.parametrize('has_bookings', [False, True])
def test_offer_cancellation_uses_only_affected_confirmed_passengers(scene, has_bookings):
    affected = []
    if has_bookings:
        previous, *affected = [book(scene, passenger) for passenger in scene.passengers]
        cancel_booking(scene, previous)
    for _ in range(2):
        CancellationService.cancel_offer(user=scene.driver, offer_id=scene.offer.pk,
                                         clock=lambda: scene.departure-timedelta(hours=5))
    event = CancellationRecord.objects.get(offer=scene.offer, booking=None)
    notices = notice_model().objects.filter(cancellation=event)
    expected = {(scene.driver.pk, 'OFFER_CANCELLED')}
    expected.update((booking.passenger_id, 'OFFER_CANCELLED') for booking in affected)
    assert set(notices.values_list('recipient_id', 'kind')) == expected
    assert notices.count() == len(expected)


@pytest.mark.parametrize('operation', ['booking', 'cancel_booking', 'cancel_offer'])
def test_notification_failure_rolls_back_original_operation(scene, monkeypatch, operation):
    model = notice_model()
    passenger = scene.passengers[0]
    booking = book(scene, passenger) if operation != 'booking' else None
    original = model.objects.bulk_create

    def fail_after_insert(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError('falha sintética após gravar aviso')

    before = list(model.objects.order_by('pk').values())
    monkeypatch.setattr(model.objects, 'bulk_create', fail_after_insert)
    with pytest.raises(RuntimeError, match='falha sintética'):
        if operation == 'booking':
            book(scene, passenger)
        elif operation == 'cancel_booking':
            cancel_booking(scene, booking, delay_hours=1)
        else:
            CancellationService.cancel_offer(user=scene.driver, offer_id=scene.offer.pk,
                                             clock=lambda: scene.departure-timedelta(hours=1))
    assert list(model.objects.order_by('pk').values()) == before
    assert not CancellationRecord.objects.exists() and not PenaltyRecord.objects.exists()
    scene.offer.refresh_from_db()
    assert scene.offer.status == RideOffer.Status.ABERTA and scene.offer.cancelled_at is None
    if booking is not None:
        booking.refresh_from_db()
        assert booking.status == RideBooking.Status.CONFIRMADA and booking.cancelled_at is None
    else:
        assert not RideBooking.objects.exists()


def test_rejected_operations_and_outer_rollback_produce_no_additional_notices(scene):
    passenger, other, _ = scene.passengers
    model = notice_model()
    with pytest.raises(RuntimeError), transaction.atomic():
        book(scene, passenger)
        raise RuntimeError('rollback externo')
    assert not model.objects.exists()

    RideOffer.objects.filter(pk=scene.offer.pk).update(seats=1)
    booking = book(scene, passenger)
    with pytest.raises(NoSeatsAvailable):
        book(scene, other)
    with pytest.raises(PermissionDenied):
        CancellationService.cancel_booking(user=other, booking_id=booking.pk)
    with pytest.raises(CancellationRefused):
        cancel_booking(scene, booking, delay_hours=0)
    assert model.objects.count() == 2 and not CancellationRecord.objects.exists()


def test_database_rejects_duplicate_or_mismatched_origin(scene):
    booking = book(scene, scene.passengers[0])
    model = notice_model()
    for kind in ('BOOKING_CONFIRMED', 'OFFER_CANCELLED'):
        duplicate = model(recipient=scene.driver, booking=booking, kind=kind)
        with pytest.raises(IntegrityError), transaction.atomic():
            model.objects.bulk_create([duplicate])
    assert model.objects.count() == 2


@pytest.mark.django_db(transaction=True)
def test_concurrent_repeated_cancellation_has_one_event_and_one_notice_per_recipient(scene):
    assert connection.vendor == 'postgresql'
    booking = book(scene, scene.passengers[0])
    barrier = Barrier(2, timeout=10)

    def worker():
        db = connections['default']
        try:
            with transaction.atomic(), db.cursor() as cursor:
                cursor.execute("SET LOCAL lock_timeout = '10s'")
                cursor.execute('SELECT pg_backend_pid()')
                pid = cursor.fetchone()[0]
                barrier.wait()
                cancel_booking(scene, booking)
            return pid
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [task.result(timeout=20) for task in [pool.submit(worker), pool.submit(worker)]]
    assert len(set(results)) == 2
    assert CancellationRecord.objects.filter(booking=booking).count() == 1
    assert notice_model().objects.filter(kind='BOOKING_CANCELLED').count() == 2


@pytest.mark.django_db(transaction=True)
def test_offer_cancel_can_notify_passenger_while_another_booking_holds_account_lock(scene, academic_user_factory):
    passenger = scene.passengers[0]
    book(scene, passenger)
    driver = academic_user_factory(role='MOTORISTA', password=None)
    driver.academic_status = 'ATIVA'
    driver.save(update_fields=['academic_status'])
    other_offer = RideOffer.objects.create(
        driver=driver, origin=scene.origin, destination=scene.destination,
        departure_at=scene.departure + timedelta(days=1), seats=1,
        vehicle_model='Sintético', vehicle_color='Azul', vehicle_plate='SINTETIC',
    )
    booking_holds_lock = Event()
    cancellation_committed = Event()

    def make_booking():
        try:
            with transaction.atomic():
                book(scene, passenger, offer=other_offer)
                booking_holds_lock.set()
                assert cancellation_committed.wait(timeout=10)
        finally:
            connections['default'].close()

    def cancel_offer():
        db = connections['default']
        try:
            assert booking_holds_lock.wait(timeout=10)
            with transaction.atomic(), db.cursor() as cursor:
                cursor.execute("SET LOCAL lock_timeout = '3s'")
                CancellationService.cancel_offer(user=scene.driver, offer_id=scene.offer.pk,
                                                 clock=lambda: scene.departure-timedelta(hours=5))
        finally:
            cancellation_committed.set()
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        reserved = pool.submit(make_booking)
        cancelled = pool.submit(cancel_offer)
        cancelled.result(timeout=20)
        reserved.result(timeout=20)
    assert notice_model().objects.filter(kind='OFFER_CANCELLED', recipient=passenger).count() == 1
    assert RideBooking.objects.filter(offer=other_offer, passenger=passenger).count() == 1
