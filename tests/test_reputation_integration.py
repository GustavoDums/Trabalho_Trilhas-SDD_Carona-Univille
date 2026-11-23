"""Feature 007/T004 (roadmap T031), REQ-003, REQ-009 e REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from threading import Barrier, Event

import pytest
from django.db import connection, connections, transaction
from django.db.models.signals import post_save

from reviews.models import ReputationProfile, RideReview
from reviews.services import review_service
from reviews.services.review_service import ReviewService
from rides.models import RideOffer
from rides.services.booking_service import BookingService


@pytest.fixture
def completed_ride(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    RideOffer.objects.filter(pk=scene.offer.pk).update(seats=2)
    BookingService.create_booking(
        passenger=scene.other, offer_id=scene.offer.pk,
        boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk,
    )
    completed_at = scene.departure + timedelta(hours=1)
    ReviewService.complete_offer(
        user=scene.driver, offer_id=scene.offer.pk, clock=lambda: completed_at,
    )
    monkeypatch.setattr('django.utils.timezone.now', lambda: completed_at)
    return scene, completed_at


def submit_review(scene, reviewer, rating):
    return ReviewService.create_review(
        user=reviewer, offer_id=scene.offer.pk, reviewed_user_id=scene.driver.pk,
        rating=rating,
    )


@pytest.mark.django_db
def test_new_review_immediately_updates_only_recipient(completed_ride):
    scene, completed_at = completed_ride
    assert not ReputationProfile.objects.exists()

    submit_review(scene, scene.passenger, 2)
    profile = ReputationProfile.objects.get(user=scene.driver)
    assert profile.score == Decimal('2.00')
    assert profile.computed_at == completed_at

    submit_review(scene, scene.other, 5)
    profile.refresh_from_db()
    assert profile.score == Decimal('3.50')
    assert ReputationProfile.objects.count() == 1


@pytest.mark.django_db
def test_new_review_recreates_missing_cache_from_all_received_reviews(completed_ride):
    scene, _ = completed_ride
    submit_review(scene, scene.passenger, 2)
    ReputationProfile.objects.filter(user=scene.driver).delete()

    submit_review(scene, scene.other, 5)

    assert ReputationProfile.objects.get(user=scene.driver).score == Decimal('3.50')


@pytest.mark.django_db
def test_reprocessing_save_signal_reuses_profile_and_does_not_count_rating_twice(completed_ride):
    scene, _ = completed_ride
    submit_review(scene, scene.passenger, 2)
    latest = submit_review(scene, scene.other, 5)
    expected = ReputationProfile.objects.get(user=scene.driver)

    post_save.send(sender=RideReview, instance=latest, created=True, raw=False, using='default')

    assert RideReview.objects.count() == 2
    assert ReputationProfile.objects.count() == 1
    cached = ReputationProfile.objects.get(user=scene.driver)
    assert (cached.pk, cached.score, cached.computed_at) == (
        expected.pk, Decimal('3.50'), expected.computed_at,
    )


@pytest.mark.django_db
def test_raw_signal_and_unchanged_save_do_not_rebuild_profile(completed_ride, monkeypatch):
    scene, completed_at = completed_ride
    review = submit_review(scene, scene.passenger, 3)
    monkeypatch.setattr('django.utils.timezone.now', lambda: completed_at + timedelta(minutes=1))

    post_save.send(sender=RideReview, instance=review, created=True, raw=True, using='default')
    review.save()

    assert ReputationProfile.objects.get(user=scene.driver).computed_at == completed_at


@pytest.mark.django_db
@pytest.mark.parametrize('has_profile', [False, True])
def test_outer_rollback_restores_review_and_projection(completed_ride, has_profile):
    scene, _ = completed_ride
    if has_profile:
        submit_review(scene, scene.passenger, 2)

    with pytest.raises(RuntimeError, match='rollback sintético'), transaction.atomic():
        submit_review(scene, scene.other, 5)
        expected_score = Decimal('3.50' if has_profile else '5.00')
        assert ReputationProfile.objects.get(user=scene.driver).score == expected_score
        raise RuntimeError('rollback sintético')

    assert not RideReview.objects.filter(reviewer=scene.other).exists()
    if has_profile:
        assert ReputationProfile.objects.get(user=scene.driver).score == Decimal('2.00')
    else:
        assert not ReputationProfile.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_projection_failure_rolls_back_direct_review_save(completed_ride, monkeypatch):
    scene, completed_at = completed_ride
    save_profile = ReputationProfile.save

    def fail_after_save(profile, *args, **kwargs):
        save_profile(profile, *args, **kwargs)
        raise RuntimeError('falha sintética da projeção')

    monkeypatch.setattr(ReputationProfile, 'save', fail_after_save)

    with pytest.raises(RuntimeError, match='falha sintética da projeção'):
        RideReview.objects.create(
            offer=scene.offer, reviewer=scene.passenger, reviewed_user=scene.driver,
            rating=2, created_at=completed_at,
        )

    assert not RideReview.objects.exists()
    assert not ReputationProfile.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_concurrent_review_saves_rebuild_one_profile_from_both_sources(completed_ride):
    assert connection.vendor == 'postgresql'
    scene, completed_at = completed_ride
    barrier = Barrier(2, timeout=10)

    def save_review(reviewer_id, rating):
        db = connections['default']
        try:
            with transaction.atomic(), db.cursor() as cursor:
                cursor.execute("SET LOCAL lock_timeout = '10s'")
                cursor.execute('SELECT pg_backend_pid(), txid_current()')
                backend, txid = cursor.fetchone()
                barrier.wait()
                RideReview.objects.create(
                    offer_id=scene.offer.pk, reviewer_id=reviewer_id,
                    reviewed_user_id=scene.driver.pk, rating=rating, created_at=completed_at,
                )
            return backend, txid
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(save_review, scene.passenger.pk, 2)
        second = pool.submit(save_review, scene.other.pk, 5)
        first_backend, first_txid = first.result(timeout=25)
        second_backend, second_txid = second.result(timeout=25)

    assert first_backend != second_backend and first_txid != second_txid
    assert RideReview.objects.count() == 2
    assert ReputationProfile.objects.count() == 1
    assert ReputationProfile.objects.get(user=scene.driver).score == Decimal('3.50')


@pytest.mark.django_db(transaction=True)
def test_direct_save_can_commit_while_review_service_holds_offer_lock(completed_ride, monkeypatch):
    scene, completed_at = completed_ride
    direct_projection_ready = Event()
    service_has_offer_lock = Event()
    get_accounts = review_service._accounts

    def get_accounts_after_offer_lock(*ids):
        service_has_offer_lock.set()
        return get_accounts(*ids)

    monkeypatch.setattr(review_service, '_accounts', get_accounts_after_offer_lock)

    def direct_save():
        try:
            with transaction.atomic():
                RideReview.objects.create(
                    offer_id=scene.offer.pk, reviewer_id=scene.passenger.pk,
                    reviewed_user_id=scene.driver.pk, rating=2, created_at=completed_at,
                )
                direct_projection_ready.set()
                assert service_has_offer_lock.wait(timeout=10)
        finally:
            connections['default'].close()

    def service_save():
        try:
            assert direct_projection_ready.wait(timeout=10)
            submit_review(scene, scene.other, 5)
        finally:
            connections['default'].close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        direct = pool.submit(direct_save)
        from_service = pool.submit(service_save)
        direct.result(timeout=20)
        from_service.result(timeout=20)

    assert RideReview.objects.count() == 2
    assert ReputationProfile.objects.get(user=scene.driver).score == Decimal('3.50')
