"""Feature 008/T002 (roadmap T032), REQ-003, REQ-010 e REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal, localcontext
from threading import Barrier, Event

import pytest
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, connections, transaction
from django.db.models.deletion import ProtectedError

from reviews.models import ConductProfile, PenaltyRecord, ReputationProfile, RideReview
from reviews.services.penalty_service import PenaltyService
from reviews.services.reputation_service import ReputationService, calculate_score
from rides.models import CancellationRecord, RideBooking, RideOffer
from rides.services import cancellation_service
from rides.services.cancellation_service import CancellationService


def penalty_model():
    return apps.get_model('reviews', 'PenaltyRecord')


def conduct_model():
    return apps.get_model('reviews', 'ConductProfile')


def cancellation_data(scene, *, cancel_offer):
    event = CancellationRecord.objects.create(
        actor=scene.driver if cancel_offer else scene.passenger,
        offer=scene.offer, booking=None if cancel_offer else scene.booking,
        occurred_at=scene.departure-timedelta(hours=1),
        classification=CancellationRecord.Classification.TARDIO,
    )
    return dict(subject=event.actor, offer=event.offer, booking=event.booking, cancellation=event,
                kind='CANCELAMENTO_TARDIO', source_key=f'cancellation:{event.pk}',
                occurred_at=event.occurred_at, delta=Decimal('-0.20'))


def no_show_data(scene, *, offer=None, booking=None, when=None):
    offer = scene.offer if offer is None else offer
    booking = scene.booking if booking is None else booking
    when = scene.departure if when is None else when
    return dict(subject=booking.passenger, actor=offer.driver, offer=offer, booking=booking,
                kind='NO_SHOW', source_key=f'no-show:{offer.pk}:{booking.passenger_id}',
                occurred_at=when, reported_at=when+timedelta(hours=1), delta=Decimal('-0.50'))


def additional_booking(scene, *, departure=None):
    offer = RideOffer.objects.create(
        driver=scene.driver, origin=scene.points[0], destination=scene.points[-1],
        departure_at=departure or scene.departure, seats=1, vehicle_model='Sintético',
        vehicle_color='Azul', vehicle_plate='SINTETIC',
    )
    return RideBooking.objects.create(offer=offer, passenger=scene.passenger,
                                      boarding_point=scene.points[0], alighting_point=scene.points[-1])


@pytest.mark.django_db
@pytest.mark.parametrize('cancel_offer', [False, True])
def test_late_cancellation_keeps_event_and_deducts_twenty_cents(cancellation_scene, cancel_offer):
    values = cancellation_data(cancellation_scene, cancel_offer=cancel_offer)
    penalty = penalty_model().objects.create(**values)
    penalty.refresh_from_db()

    assert penalty.actor is None and penalty.automatic_rating is None
    assert penalty.cancellation == values['cancellation']
    assert penalty.booking == values['booking']
    assert penalty.delta == Decimal('-0.20')
    assert penalty_model().apply_deductions(Decimal('4.80'), [penalty, penalty]) == Decimal('4.60')
    with pytest.raises(ProtectedError):
        penalty.cancellation.delete()


@pytest.mark.django_db
@pytest.mark.parametrize('absent_driver', [False, True])
def test_no_show_supplies_one_rating_and_one_fixed_deduction(cancellation_scene, absent_driver):
    values = no_show_data(cancellation_scene)
    if absent_driver:
        values['subject'], values['actor'] = values['actor'], values['subject']
    penalty = penalty_model().objects.create(**values)

    assert penalty.automatic_rating == 1
    average = calculate_score([5, 5, 5, penalty.automatic_rating])
    assert average == Decimal('4.00')
    with localcontext() as context:
        context.prec = 1
        assert penalty_model().apply_deductions(average, [penalty, penalty]) == Decimal('3.50')
    assert penalty_model().apply_deductions(Decimal('0.25'), [penalty]) == Decimal('0.00')
    assert penalty_model().apply_deductions(Decimal('5.00'), []) == Decimal('5.00')
    with pytest.raises(ProtectedError):
        penalty.booking.delete()


@pytest.mark.django_db
@pytest.mark.parametrize('field', ['actor', 'subject', 'booking', 'reported_at', 'occurred_at', 'delta', 'kind'])
def test_rejects_inconsistent_no_show(cancellation_scene, field):
    scene = cancellation_scene
    values = no_show_data(scene)
    overrides = {
        'actor': scene.other,
        'subject': scene.other,
        'booking': None,
        'reported_at': scene.departure-timedelta(seconds=1),
        'occurred_at': scene.departure.replace(tzinfo=None),
        'delta': Decimal('-0.20'),
        'kind': 'DESCONHECIDO',
    }
    values[field] = overrides[field]
    with pytest.raises(ValidationError):
        penalty_model().objects.create(**values)
    assert not penalty_model().objects.exists()


@pytest.mark.django_db
def test_no_show_requires_confirmed_booking(cancellation_scene):
    scene = cancellation_scene
    CancellationService.cancel_booking(user=scene.passenger, booking_id=scene.booking.pk,
                                       clock=lambda: scene.departure-timedelta(hours=1))
    with pytest.raises(ValidationError, match='reserva confirmada'):
        penalty_model().objects.create(**no_show_data(scene))


@pytest.mark.django_db
@pytest.mark.parametrize('field', ['classification', 'actor', 'subject', 'offer', 'booking', 'occurred_at'])
def test_rejects_inconsistent_cancellation_origin(cancellation_scene, field):
    scene = cancellation_scene
    values = cancellation_data(scene, cancel_offer=False)
    if field == 'classification':
        CancellationRecord.objects.filter(pk=values['cancellation'].pk).update(
            classification=CancellationRecord.Classification.TEMPESTIVO,
        )
    else:
        overrides = {'actor': scene.other, 'subject': scene.other, 'booking': None,
                     'occurred_at': scene.departure, 'offer': additional_booking(scene).offer}
        values[field] = overrides[field]
    with pytest.raises(ValidationError):
        penalty_model().objects.create(**values)


@pytest.mark.django_db
@pytest.mark.parametrize('conflict', ['key', 'no_show', 'cancellation', 'delta', 'shape'])
def test_database_constraints_preserve_one_valid_record_per_origin(cancellation_scene, conflict):
    scene = cancellation_scene
    model = penalty_model()
    values = cancellation_data(scene, cancel_offer=False) if conflict == 'cancellation' else no_show_data(scene)
    model.objects.create(**values)
    if conflict == 'key':
        booking = additional_booking(scene)
        duplicate = no_show_data(scene, offer=booking.offer, booking=booking)
        duplicate['source_key'] = values['source_key']
    else:
        duplicate = dict(values, source_key='alternate-key')
        if conflict in {'delta', 'shape'}:
            booking = additional_booking(scene)
            duplicate = no_show_data(scene, offer=booking.offer, booking=booking)
            if conflict == 'delta':
                duplicate['delta'] = Decimal('-0.20')
            else:
                duplicate['actor'] = None
    with pytest.raises(IntegrityError), transaction.atomic():
        model.objects.bulk_create([model(**duplicate)])
    assert model.objects.count() == 1


@pytest.mark.django_db
def test_third_no_show_in_inclusive_thirty_day_window_projects_fourteen_day_suspension(cancellation_scene):
    scene = cancellation_scene
    model = penalty_model()
    conduct = conduct_model().objects.create(user=scene.passenger)
    at = scene.departure
    for when in (at-timedelta(days=30, seconds=1), at-timedelta(days=30), at-timedelta(days=1)):
        booking = additional_booking(scene, departure=when)
        model.objects.create(**no_show_data(scene, offer=booking.offer, booking=booking, when=when))
    assert conduct.suspension_after_no_show(at=at) is None

    future = additional_booking(scene, departure=at+timedelta(seconds=1))
    model.objects.create(**no_show_data(scene, offer=future.offer, booking=future, when=at+timedelta(seconds=1)))
    assert conduct.suspension_after_no_show(at=at) is None

    model.objects.create(**no_show_data(scene))
    until = conduct.suspension_after_no_show(at=at)
    assert until == at+timedelta(days=14)
    assert conduct.suspension_after_no_show(at=at+timedelta(seconds=2)) is None
    conduct.refresh_from_db()
    assert conduct.suspended_until is None
    conduct.suspended_until = until
    conduct.save()
    assert conduct.is_suspended_at(at=until-timedelta(seconds=1))
    assert not conduct.is_suspended_at(at=until)
    scene.passenger.refresh_from_db()
    assert scene.passenger.academic_status == 'ATIVA' and scene.passenger.is_active


@pytest.mark.django_db
def test_conduct_is_optional_unique_protected_and_requires_aware_instants(cancellation_scene):
    user = cancellation_scene.other
    model = conduct_model()
    conduct = model.objects.create(user=user)
    now = cancellation_scene.departure
    naive = now.replace(tzinfo=None)
    assert not conduct.is_suspended_at(at=now)
    for method in (conduct.is_suspended_at, conduct.suspension_after_no_show):
        with pytest.raises(ValidationError):
            method(at=naive)
    conduct.suspended_until = naive
    with pytest.raises(ValidationError):
        conduct.save()
    with pytest.raises(ProtectedError):
        user.delete()
    with pytest.raises(IntegrityError), transaction.atomic():
        model.objects.bulk_create([model(user=user, suspended_until=now)])


@pytest.mark.django_db(transaction=True)
def test_concurrent_duplicate_no_show_preserves_one_event(cancellation_scene):
    assert connection.vendor == 'postgresql'
    model = penalty_model()
    payload = no_show_data(cancellation_scene)
    barrier = Barrier(2, timeout=10)

    def insert(key):
        try:
            with transaction.atomic(), connections['default'].cursor() as cursor:
                cursor.execute("SET LOCAL lock_timeout = '10s'")
                barrier.wait()
                model.objects.bulk_create([model(**dict(payload, source_key=key))])
            return True
        except IntegrityError:
            return False
        finally:
            connections['default'].close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(insert, ['first-report', 'second-report'])) == [False, True]
    assert model.objects.count() == 1


@pytest.mark.django_db
def test_rollback_preserves_existing_reputation_and_conduct(cancellation_scene):
    scene = cancellation_scene
    profile = apps.get_model('reviews', 'ReputationProfile').objects.create(user=scene.passenger)
    conduct = conduct_model().objects.create(user=scene.passenger)
    with pytest.raises(RuntimeError, match='rollback'), transaction.atomic():
        penalty_model().objects.create(**no_show_data(scene))
        raise RuntimeError('rollback')
    profile.refresh_from_db()
    conduct.refresh_from_db()
    assert profile.score == Decimal('5.00') and conduct.suspended_until is None
    assert not penalty_model().objects.exists()


def cancel(scene, *, at, cancel_offer=False, booking=None):
    if cancel_offer:
        return CancellationService.cancel_offer(user=scene.driver, offer_id=scene.offer.pk, clock=lambda: at)
    booking = scene.booking if booking is None else booking
    return CancellationService.cancel_booking(user=scene.passenger, booking_id=booking.pk, clock=lambda: at)


def add_rating(scene, *, at, rating):
    booking = additional_booking(scene)
    return RideReview.objects.create(offer=booking.offer, reviewer=scene.driver,
                                     reviewed_user=scene.passenger, created_at=at, rating=rating)


@pytest.mark.django_db
@pytest.mark.parametrize('cancel_offer', [False, True])
def test_real_late_cancellation_penalizes_only_the_actor_once(cancellation_scene, cancel_offer):
    scene = cancellation_scene
    at = scene.departure-timedelta(hours=1)
    actor = scene.driver if cancel_offer else scene.passenger
    other = scene.passenger if cancel_offer else scene.driver

    for _ in range(2):
        cancel(scene, at=at, cancel_offer=cancel_offer)

    event = CancellationRecord.objects.get(actor=actor)
    penalty = PenaltyRecord.objects.get(cancellation=event)
    assert penalty.subject == actor and penalty.delta == Decimal('-0.20') and penalty.actor is None
    assert penalty.occurred_at == at and penalty.booking_id == event.booking_id
    assert ReputationProfile.objects.get(user=actor).score == Decimal('4.80')
    assert not ReputationProfile.objects.filter(user=other).exists()
    assert not ConductProfile.objects.exists()
    scene.booking.refresh_from_db()
    assert scene.booking.status == RideBooking.Status.CANCELADA


@pytest.mark.django_db
@pytest.mark.parametrize('cancel_offer', [False, True])
def test_cancellation_at_deadline_and_explicit_replay_have_no_penalty(cancellation_scene, cancel_offer):
    scene = cancellation_scene
    at = scene.departure-timedelta(hours=4 if cancel_offer else 2)
    cancel(scene, at=at, cancel_offer=cancel_offer)

    event = CancellationRecord.objects.get()
    assert event.classification == CancellationRecord.Classification.TEMPESTIVO
    assert PenaltyService.apply_cancellation(cancellation_id=event.pk) is None
    assert not PenaltyRecord.objects.exists() and not ReputationProfile.objects.exists()


@pytest.mark.django_db
def test_legacy_late_cancellation_can_be_replayed_without_duplication_or_historical_rewind(
    cancellation_scene, monkeypatch,
):
    scene = cancellation_scene
    event = cancellation_data(scene, cancel_offer=False)['cancellation']
    at = event.occurred_at+timedelta(seconds=1)
    monkeypatch.setattr('django.utils.timezone.now', lambda: at)
    add_rating(scene, at=at, rating=4)

    first = PenaltyService.apply_cancellation(cancellation_id=event.pk)
    ReputationProfile.objects.filter(user=scene.passenger).delete()
    second = PenaltyService.apply_cancellation(cancellation_id=event.pk)

    assert first.pk == second.pk and PenaltyRecord.objects.count() == 1
    assert ReputationProfile.objects.get(user=scene.passenger).score == Decimal('3.80')
    assert ReputationService.rebuild(user_id=scene.passenger.pk, at=event.occurred_at).score == Decimal('4.80')
    assert ReputationService.rebuild(
        user_id=scene.passenger.pk, at=event.occurred_at-timedelta(microseconds=1),
    ).score == Decimal('5.00')


@pytest.mark.django_db
def test_received_review_signal_rebuilds_score_without_losing_late_cancellation_deduction(
    cancellation_scene, monkeypatch,
):
    scene = cancellation_scene
    at = scene.departure-timedelta(hours=1)
    for rating in [5, 5, 5, 5, 4]:
        add_rating(scene, at=at-timedelta(minutes=1), rating=rating)
    cancel(scene, at=at)
    assert ReputationProfile.objects.get(user=scene.passenger).score == Decimal('4.60')

    next_rating_at = at+timedelta(minutes=1)
    monkeypatch.setattr('django.utils.timezone.now', lambda: next_rating_at)
    add_rating(scene, at=next_rating_at, rating=3)

    assert ReputationProfile.objects.get(user=scene.passenger).score == Decimal('4.30')
    assert RideReview.objects.count() == 6 and PenaltyRecord.objects.count() == 1


@pytest.mark.django_db
def test_rebuild_includes_existing_no_show_once_in_rating_window_and_in_deductions(cancellation_scene):
    scene = cancellation_scene
    at = scene.departure
    for _ in range(20):
        add_rating(scene, at=at-timedelta(seconds=1), rating=5)
    PenaltyRecord.objects.create(**no_show_data(scene))
    rebuild = ReputationService.rebuild

    assert rebuild(user_id=scene.passenger.pk, at=at-timedelta(microseconds=1)).score == Decimal('5.00')
    assert rebuild(user_id=scene.passenger.pk, at=at).score == Decimal('4.30')
    add_rating(scene, at=at+timedelta(seconds=1), rating=5)
    assert rebuild(user_id=scene.passenger.pk, at=at+timedelta(seconds=1)).score == Decimal('4.30')
    add_rating(scene, at=at, rating=5)
    assert rebuild(user_id=scene.passenger.pk, at=at).score == Decimal('4.30')
    assert RideReview.objects.count() == 22 and not ConductProfile.objects.exists()


@pytest.mark.django_db
def test_mutual_rating_wins_the_last_slot_on_timestamp_tie_but_no_show_delta_still_applies(cancellation_scene):
    scene = cancellation_scene
    at = scene.departure
    for _ in range(20):
        add_rating(scene, at=at, rating=5)
    PenaltyRecord.objects.create(**no_show_data(scene))
    assert ReputationService.rebuild(user_id=scene.passenger.pk, at=at).score == Decimal('4.50')


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('cancel_offer', [False, True])
def test_rebuild_failure_rolls_back_real_cancellation_event_and_penalty(cancellation_scene, monkeypatch, cancel_offer):
    scene = cancellation_scene
    at = scene.departure-timedelta(hours=1)
    actor = scene.driver if cancel_offer else scene.passenger
    profile = ReputationProfile.objects.create(user=actor)
    profile_save = ReputationProfile.save

    def fail_after_save(instance, *args, **kwargs):
        profile_save(instance, *args, **kwargs)
        raise RuntimeError('falha sintética no recálculo')

    monkeypatch.setattr(ReputationProfile, 'save', fail_after_save)
    with pytest.raises(RuntimeError, match='falha sintética no recálculo'):
        cancel(scene, at=at, cancel_offer=cancel_offer)

    scene.booking.refresh_from_db()
    scene.offer.refresh_from_db()
    profile.refresh_from_db()
    assert scene.booking.status == RideBooking.Status.CONFIRMADA and scene.booking.cancelled_at is None
    assert scene.offer.status == RideOffer.Status.ABERTA and scene.offer.cancelled_at is None
    assert profile.score == Decimal('5.00')
    assert not CancellationRecord.objects.exists() and not PenaltyRecord.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('same_event', [True, False])
def test_cancellation_workers_commit_exactly_one_effect_per_late_event(cancellation_scene, same_event):
    assert connection.vendor == 'postgresql'
    scene = cancellation_scene
    at = scene.departure-timedelta(hours=1)
    first = scene.booking
    second = first if same_event else additional_booking(scene)
    barrier = Barrier(2, timeout=10)

    def worker(booking):
        db = connections['default']
        try:
            with transaction.atomic(), db.cursor() as cursor:
                cursor.execute("SET LOCAL lock_timeout = '10s'")
                cursor.execute('SELECT pg_backend_pid()')
                pid = cursor.fetchone()[0]
                barrier.wait()
                cancel(scene, at=at, booking=booking)
                return pid
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert len(set(pool.map(worker, [first, second]))) == 2

    expected_count = 1 if same_event else 2
    assert CancellationRecord.objects.count() == PenaltyRecord.objects.count() == expected_count
    expected_score = Decimal('4.80' if same_event else '4.60')
    assert ReputationProfile.objects.get(user=scene.passenger).score == expected_score


@pytest.mark.django_db(transaction=True)
def test_late_cancellation_and_direct_review_rebuild_without_blocking_fk_validation(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    at = scene.departure-timedelta(hours=1)
    monkeypatch.setattr('django.utils.timezone.now', lambda: at)
    review_has_user_lock = Event()
    cancellation_has_offer_lock = Event()
    get_user_model = cancellation_service.get_user_model

    def get_cancellation_accounts():
        cancellation_has_offer_lock.set()
        return get_user_model()

    monkeypatch.setattr(cancellation_service, 'get_user_model', get_cancellation_accounts)

    def save_review():
        try:
            with transaction.atomic():
                RideReview.objects.create(
                    offer=scene.offer, reviewer=scene.driver,
                    reviewed_user=scene.passenger, rating=4, created_at=at,
                )
                review_has_user_lock.set()
                assert cancellation_has_offer_lock.wait(timeout=10)
        finally:
            connections['default'].close()

    def cancel_booking():
        try:
            assert review_has_user_lock.wait(timeout=10)
            cancel(scene, at=at)
        finally:
            connections['default'].close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        direct = pool.submit(save_review)
        cancellation = pool.submit(cancel_booking)
        direct.result(timeout=20)
        cancellation.result(timeout=20)

    assert RideReview.objects.count() == PenaltyRecord.objects.count() == 1
    assert ReputationProfile.objects.get(user=scene.passenger).score == Decimal('3.80')
