"""Feature 007/T002 unificada — roadmap T030; REQ-009/REQ-003/REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal, localcontext
from importlib import import_module
from threading import Barrier
from unittest.mock import Mock

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, connections, transaction, close_old_connections
from django.db.models.deletion import ProtectedError

from rides.models import RideOffer
from rides.services.booking_service import BookingService
from reviews.models import RideReview
from reviews.services.review_service import ReviewService


def profile_model():
    return apps.get_model('reviews', 'ReputationProfile')


def reputation_api():
    return import_module('reviews.services.reputation_service')


def rebuild(scene, **overrides):
    values = dict(user_id=scene.driver.pk, at=scene.departure+timedelta(hours=3))
    values.update(overrides)
    return reputation_api().ReputationService.rebuild(**values)


def received_reviews(scene, ratings, *, same_time=False):
    """Fontes criadas pelo serviço de avaliação, com participação e término válidos."""
    result = []
    for index, rating in enumerate(ratings):
        offer = scene.offer if index == 0 else RideOffer.objects.create(
            driver=scene.driver, origin=scene.points[0], destination=scene.points[-1],
            departure_at=scene.departure, seats=1, vehicle_model='Veículo Sintético',
            vehicle_color='Azul', vehicle_plate='PRIVADA')
        if index:
            BookingService.create_booking(
                passenger=scene.passenger, offer_id=offer.pk,
                boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk)
        ReviewService.complete_offer(user=scene.driver, offer_id=offer.pk,
                                     clock=lambda: scene.departure+timedelta(hours=1))
        created = scene.departure+timedelta(hours=2, seconds=0 if same_time else index)
        result.append(ReviewService.create_review(
            user=scene.passenger, offer_id=offer.pk, reviewed_user_id=scene.driver.pk,
            rating=rating, clock=lambda: created))
    return result


@pytest.mark.parametrize('ratings,expected', [
    ([], '5.00'), ([5,5,4,5,4], '4.60'), ([5,5,5,1], '4.00'),
    ([1], '1.00'), ([4], '4.00'), ([5,4,4], '4.33'),
    ([5,4,4,4,4,4,4,4], '4.13'), ([5]*20, '5.00'),
])
def test_calculation_examples_and_half_up_without_virtual_initial_rating(ratings, expected):
    actual = reputation_api().calculate_score(ratings)
    assert actual == Decimal(expected) and isinstance(actual, Decimal)
    assert actual.as_tuple().exponent == -2


@pytest.mark.parametrize('ratings', [None, [0], [6], [True], [4.5], ['5'], [None], [5]*21])
def test_calculation_rejects_noncanonical_selected_ratings(ratings):
    with pytest.raises(ValidationError):
        reputation_api().calculate_score(ratings)


def test_calculation_is_independent_of_callers_decimal_precision():
    with localcontext() as context:
        context.prec = 2
        assert reputation_api().calculate_score([5,4,4,4,4,4,4,4]) == Decimal('4.13')


@pytest.mark.django_db
def test_profile_default_decimal_one_to_one_and_protection(academic_user_factory):
    user = academic_user_factory(password=None)
    profile = profile_model().objects.create(user=user)
    profile.refresh_from_db()
    assert profile.score == Decimal('5.00') and profile.computed_at is None
    assert profile.user_id == user.pk and user.reputation_profile.pk == profile.pk
    assert profile_model()._meta.get_field('score').decimal_places == 2
    assert profile_model()._meta.get_field('score').max_digits == 3
    assert profile_model()._meta.get_field('user').one_to_one
    with pytest.raises(ProtectedError):
        user.delete()


@pytest.mark.django_db
@pytest.mark.parametrize('score', [Decimal('0.00'), Decimal('4.60'), Decimal('5.00')])
def test_profile_accepts_exact_stored_range(academic_user_factory, score):
    user = academic_user_factory(password=None)
    result = profile_model().objects.create(user=user, score=score)
    result.refresh_from_db()
    assert result.score == score


@pytest.mark.django_db
@pytest.mark.parametrize('score', ['-0.01', '5.01', '4.125', 'NaN', 'Infinity', 4.6, True, None])
def test_profile_rejects_out_of_range_or_inexact_values(academic_user_factory, score):
    user = academic_user_factory(password=None)
    with pytest.raises(ValidationError):
        profile_model().objects.create(user=user, score=score)
    assert not profile_model().objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize('invalid', ['duplicate', 'negative', 'above_max'])
def test_database_range_and_one_to_one_constraints(academic_user_factory, invalid):
    first = academic_user_factory(password=None)
    profile_model().objects.create(user=first)
    other = academic_user_factory(password=None)
    values = dict(user=first if invalid == 'duplicate' else other,
                  score=Decimal('-0.01' if invalid == 'negative' else '5.01' if invalid == 'above_max' else '5.00'))
    with pytest.raises(IntegrityError), transaction.atomic():
        profile_model().objects.bulk_create([profile_model()(**values)])
    assert profile_model().objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize('ratings,expected', [([], '5.00'), ([5,5,4,5,4], '4.60'), ([5,5,5,1], '4.00')])
def test_rebuild_examples_and_repeated_execution_preserve_sources(cancellation_scene, ratings, expected):
    scene = cancellation_scene
    received_reviews(scene, ratings)
    assert not profile_model().objects.exists()  # T031 não conectada nesta tarefa.
    before = list(RideReview.objects.values())
    first = rebuild(scene)
    assert first.score == Decimal(expected)
    assert first.computed_at == scene.departure+timedelta(hours=3)
    second = rebuild(scene)
    assert second.pk == first.pk and second.score == first.score and second.computed_at == first.computed_at
    assert profile_model().objects.count() == 1 and list(RideReview.objects.values()) == before


@pytest.mark.django_db
def test_twenty_first_review_evicts_oldest_and_reference_is_inclusive(cancellation_scene):
    scene = cancellation_scene
    rows = received_reviews(scene, [1]+[5]*20)
    assert rebuild(scene, at=rows[-2].created_at).score == Decimal('4.80')
    assert rebuild(scene, at=rows[-1].created_at).score == Decimal('5.00')
    assert rebuild(scene, at=rows[0].created_at-timedelta(microseconds=1)).score == Decimal('5.00')
    assert RideReview.objects.count() == 21


@pytest.mark.django_db
def test_equal_timestamps_use_primary_key_as_deterministic_tiebreak(cancellation_scene):
    scene = cancellation_scene
    received_reviews(scene, [1]+[5]*20, same_time=True)
    assert rebuild(scene).score == Decimal('5.00')


@pytest.mark.django_db
def test_reviews_from_same_offer_each_have_equal_weight(cancellation_scene):
    scene = cancellation_scene
    RideOffer.objects.filter(pk=scene.offer.pk).update(seats=2)
    BookingService.create_booking(passenger=scene.other, offer_id=scene.offer.pk,
        boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk)
    ReviewService.complete_offer(user=scene.driver, offer_id=scene.offer.pk,
                                 clock=lambda: scene.departure+timedelta(hours=1))
    for actor, rating in ((scene.passenger, 1), (scene.other, 5)):
        ReviewService.create_review(user=actor, offer_id=scene.offer.pk, reviewed_user_id=scene.driver.pk,
            rating=rating, clock=lambda: scene.departure+timedelta(hours=2))
    assert rebuild(scene).score == Decimal('3.00')


@pytest.mark.django_db
def test_no_thirty_day_expiration_and_other_recipients_are_not_counted(cancellation_scene):
    scene = cancellation_scene
    row = received_reviews(scene, [2])[0]
    ReviewService.create_review(user=scene.driver, offer_id=scene.offer.pk, reviewed_user_id=scene.passenger.pk,
        rating=5, clock=lambda: row.created_at)
    assert rebuild(scene, at=row.created_at+timedelta(days=90)).score == Decimal('2.00')
    assert rebuild(scene, user_id=scene.passenger.pk, at=row.created_at).score == Decimal('5.00')


@pytest.mark.django_db
def test_historical_ratings_remain_after_account_is_disabled_and_rebuild_replaces_stale_cache(cancellation_scene):
    scene = cancellation_scene
    received_reviews(scene, [4])
    existing = profile_model().objects.create(user=scene.driver, score=Decimal('1.00'))
    get_user_model().objects.filter(pk=scene.driver.pk).update(is_active=False)
    result = rebuild(scene)
    assert result.pk == existing.pk and result.score == Decimal('4.00')


@pytest.mark.django_db
@pytest.mark.parametrize('user_id', [True, 0, -1, '1', None, 999999])
def test_rebuild_invalid_user_is_rejected_without_cache(cancellation_scene, user_id):
    with pytest.raises(ValidationError):
        rebuild(cancellation_scene, user_id=user_id)
    assert not profile_model().objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize('instant', ['naive', 'text', 'offset'])
def test_reference_requires_aware_datetime_and_normalizes_utc(cancellation_scene, instant):
    from datetime import timezone as dt_timezone
    scene = cancellation_scene
    at = scene.departure.replace(tzinfo=None) if instant == 'naive' else '2030-01-01'
    if instant == 'offset':
        at = scene.departure.astimezone(dt_timezone(timedelta(hours=-3)))
        result = rebuild(scene, at=at)
        assert result.computed_at == scene.departure and result.computed_at.utcoffset() == timedelta()
    else:
        with pytest.raises(ValidationError):
            rebuild(scene, at=at)
        assert not profile_model().objects.exists()


@pytest.mark.django_db
def test_default_reference_captures_server_clock_once(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    clock = Mock(return_value=scene.departure)
    monkeypatch.setattr('reviews.services.reputation_service.timezone.now', clock)
    result = reputation_api().ReputationService.rebuild(user_id=scene.driver.pk)
    clock.assert_called_once_with()
    assert result.computed_at == scene.departure


@pytest.mark.django_db
@pytest.mark.parametrize('existing', [False, True])
def test_rebuild_failure_rolls_back_cache_and_keeps_reviews(cancellation_scene, monkeypatch, existing):
    scene = cancellation_scene
    received_reviews(scene, [4])
    if existing:
        profile_model().objects.create(user=scene.driver, score=Decimal('1.00'))
    before_cache, before_reviews = list(profile_model().objects.values()), list(RideReview.objects.values())
    original = profile_model().save
    def fail_after_save(self, *args, **kwargs):
        original(self, *args, **kwargs)
        raise RuntimeError('Falha sintética na projeção')
    with monkeypatch.context() as patch:
        patch.setattr(profile_model(), 'save', fail_after_save)
        with pytest.raises(RuntimeError):
            rebuild(scene)
    assert list(profile_model().objects.values()) == before_cache
    assert list(RideReview.objects.values()) == before_reviews
    assert rebuild(scene).score == Decimal('4.00')


@pytest.mark.django_db(transaction=True)
def test_two_rebuilds_serialize_missing_cache_on_independent_postgresql_transactions(cancellation_scene, record_testsuite_property):
    import json
    scene = cancellation_scene
    received_reviews(scene, [5,5,4,5,4])
    assert connection.vendor == 'postgresql' and not connection.in_atomic_block
    barrier = Barrier(2, timeout=10)
    def worker():
        close_old_connections()
        try:
            with transaction.atomic():
                with connections['default'].cursor() as cursor:
                    cursor.execute("SET LOCAL lock_timeout = '10s'")
                    cursor.execute('SELECT pg_backend_pid(), txid_current()')
                    pid, txid = cursor.fetchone()
                barrier.wait()
                result = rebuild(scene)
            return str(result.score), result.pk, pid, txid
        finally:
            connections['default'].close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(worker) for _ in range(2)]
        outcomes = [future.result(timeout=20) for future in futures]
    assert all(item[0] == '4.60' for item in outcomes)
    assert len({item[1] for item in outcomes}) == 1
    assert len({item[2] for item in outcomes}) == len({item[3] for item in outcomes}) == 2
    assert profile_model().objects.count() == 1
    record_testsuite_property('reputation_rebuild_race', json.dumps(outcomes))


@pytest.mark.django_db
def test_profile_timestamp_requires_timezone_without_fabricating_default(cancellation_scene):
    scene = cancellation_scene
    with pytest.raises(ValidationError):
        profile_model().objects.create(user=scene.driver, computed_at=scene.departure.replace(tzinfo=None))
    assert not profile_model().objects.exists()
    profile = profile_model().objects.create(user=scene.driver, computed_at=scene.departure)
    assert profile.computed_at == scene.departure


def test_calculation_is_independent_of_callers_rounding_traps():
    from decimal import Inexact, ROUND_DOWN
    with localcontext() as context:
        context.rounding = ROUND_DOWN
        context.traps[Inexact] = True
        assert reputation_api().calculate_score([5,4,4,4,4,4,4,4]) == Decimal('4.13')
