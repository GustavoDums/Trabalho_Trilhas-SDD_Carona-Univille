"""Feature 008/T004 (roadmap T033), REQ-010, REQ-003 e REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from threading import Barrier

import pytest
from django.db import connection, connections
from django.core.exceptions import ValidationError
from django.test import Client
from django.urls import reverse

from reviews.models import ConductProfile, PenaltyRecord, ReputationProfile
from reviews.services.review_service import ReviewService
from rides.models import RideBooking, RideOffer

pytestmark = pytest.mark.django_db


def report_url(booking):
    return reverse('reviews:report_no_show', kwargs={'booking_id': booking.pk})


def completion_url(offer):
    return reverse('reviews:complete_ride', kwargs={'offer_id': offer.pk})


def freeze(monkeypatch, at):
    monkeypatch.setattr('django.utils.timezone.now', lambda: at)


@pytest.fixture
def completed_scene(cancellation_scene):
    scene = cancellation_scene
    finished = scene.departure + timedelta(minutes=20)
    ReviewService.complete_offer(user=scene.driver, offer_id=scene.offer.pk, clock=lambda: finished)
    return scene, finished


def test_driver_can_complete_from_my_offers_once_via_post(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    client = Client(enforce_csrf_checks=True)
    freeze(monkeypatch, scene.departure)
    client.force_login(scene.driver)
    url = completion_url(scene.offer)
    assert url.encode() in client.get(reverse('rides:my-offers')).content
    csrf = client.cookies['csrftoken'].value
    assert client.get(url).status_code == 405
    assert client.post(url).status_code == 403
    for offset in (0, 60):
        freeze(monkeypatch, scene.departure + timedelta(seconds=offset))
        response = client.post(url, {'csrfmiddlewaretoken': csrf, 'completed_at': '2000-01-01'})
        assert response.status_code == 302 and response.url == reverse('rides:my-offers')
    scene.offer.refresh_from_db()
    assert scene.offer.completed_at == scene.departure


@pytest.mark.parametrize('who,expected', [('passenger', 403), ('driver', 400)])
def test_completion_rejects_wrong_role_and_before_departure(cancellation_scene, monkeypatch, who, expected):
    scene = cancellation_scene
    freeze(monkeypatch, scene.departure - timedelta(seconds=1))
    client = Client()
    client.force_login(getattr(scene, who))
    assert client.post(completion_url(scene.offer)).status_code == expected
    scene.offer.refresh_from_db()
    assert scene.offer.completed_at is None


def test_confirmed_driver_can_report_with_csrf_and_server_evidence(completed_scene, monkeypatch):
    scene, finished = completed_scene
    freeze(monkeypatch, finished)
    client = Client(enforce_csrf_checks=True)
    client.force_login(scene.driver)
    url = report_url(scene.booking)
    assert url.encode() in client.get(reverse('rides:my_bookings')).content
    page = client.get(url)
    assert page.status_code == 200
    assert scene.passenger.email.encode() not in page.content
    assert scene.offer.vehicle_plate.encode() not in page.content
    assert not PenaltyRecord.objects.exists()
    assert client.post(url, {'declared': 'yes'}).status_code == 403
    csrf = client.cookies['csrftoken'].value
    assert client.post(url, {'csrfmiddlewaretoken': csrf, 'declared': 'no'}).status_code == 400
    assert not PenaltyRecord.objects.exists()

    for _ in range(2):
        response = client.post(url, {
            'csrfmiddlewaretoken': csrf, 'declared': 'yes', 'subject_id': scene.other.pk,
            'actor_id': scene.other.pk, 'reported_at': '2000-01-01', 'next': 'https://example.invalid',
        })
        assert response.status_code == 302 and response.url == reverse('rides:my_bookings')
    penalty = PenaltyRecord.objects.get()
    assert penalty.actor == scene.driver and penalty.subject == scene.passenger
    assert penalty.reported_at == finished and penalty.occurred_at == scene.departure + timedelta(minutes=10)
    assert penalty.booking == scene.booking and penalty.automatic_rating == 1
    scene.booking.refresh_from_db()
    assert scene.booking.no_show_at == penalty.occurred_at
    assert ReputationProfile.objects.get(user=scene.passenger).score == Decimal('0.50')


@pytest.mark.parametrize('use_completion', [False, True])
@pytest.mark.parametrize('when,expected', [('before', 400), ('first', 302), ('last', 302), ('after', 400)])
def test_report_window_inclusive_in_both_directions(
    cancellation_scene, monkeypatch, use_completion, when, expected,
):
    scene = cancellation_scene
    actor = scene.passenger
    starts = scene.departure + timedelta(minutes=10)
    if use_completion:
        actor = scene.driver
        starts = scene.departure + timedelta(minutes=30)
        ReviewService.complete_offer(user=scene.driver, offer_id=scene.offer.pk, clock=lambda: starts)
    instant = starts + {
        'before': timedelta(seconds=-1), 'first': timedelta(),
        'last': timedelta(hours=2), 'after': timedelta(hours=2, seconds=1),
    }[when]
    freeze(monkeypatch, instant)
    client = Client()
    client.force_login(actor)
    assert client.post(report_url(scene.booking), {'declared': 'yes'}).status_code == expected
    assert PenaltyRecord.objects.count() == (expected == 302)
    if not use_completion and expected == 302:
        assert PenaltyRecord.objects.get().subject == scene.driver
        scene.offer.refresh_from_db()
        assert scene.offer.completed_at is None


@pytest.mark.parametrize('issue,expected', [
    ('visitor', 302), ('outsider', 403), ('inactive', 302), ('cancelled', 400),
    ('waypoint', 400), ('missing_completion', 400), ('still_waiting', 400),
])
def test_no_report_for_ineligible_actor_booking_or_time(cancellation_scene, monkeypatch, issue, expected):
    scene = cancellation_scene
    finished = scene.departure + timedelta(minutes=3)
    if issue != 'missing_completion':
        ReviewService.complete_offer(user=scene.driver, offer_id=scene.offer.pk, clock=lambda: finished)
    freeze(monkeypatch, finished if issue == 'still_waiting' else finished + timedelta(minutes=10))
    if issue == 'cancelled':
        RideBooking.objects.filter(pk=scene.booking.pk).update(status=RideBooking.Status.CANCELADA)
    if issue == 'waypoint':
        RideBooking.objects.filter(pk=scene.booking.pk).update(boarding_point=scene.points[1])
    client = Client()
    if issue != 'visitor':
        client.force_login(scene.other if issue == 'outsider' else scene.driver)
    if issue == 'inactive':
        type(scene.driver).objects.filter(pk=scene.driver.pk).update(is_active=False)
    for response in (client.get(report_url(scene.booking)),
                     client.post(report_url(scene.booking), {'declared': 'yes'})):
        assert response.status_code == expected
    assert not PenaltyRecord.objects.exists()


def test_reporter_can_record_absence_after_counterpart_account_is_disabled(completed_scene, monkeypatch):
    scene, finished = completed_scene
    freeze(monkeypatch, finished)
    type(scene.passenger).objects.filter(pk=scene.passenger.pk).update(is_active=False)
    client = Client()
    client.force_login(scene.driver)
    assert client.post(report_url(scene.booking), {'declared': 'yes'}).status_code == 302
    assert PenaltyRecord.objects.get().subject_id == scene.passenger.pk


def test_driver_no_show_is_unique_across_bookings_and_prevents_reviews(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    RideOffer.objects.filter(pk=scene.offer.pk).update(seats=2)
    second_booking = RideBooking.objects.create(
        offer=scene.offer, passenger=scene.other,
        boarding_point=scene.points[0], alighting_point=scene.points[-1],
    )
    at = scene.departure + timedelta(minutes=10)
    freeze(monkeypatch, at)
    client = Client()
    for actor, booking in ((scene.passenger, scene.booking), (scene.other, second_booking)):
        client.force_login(actor)
        assert client.post(report_url(booking), {'declared': 'yes'}).status_code == 302
    penalty = PenaltyRecord.objects.get()
    assert penalty.actor_id == scene.passenger.pk and penalty.subject_id == scene.driver.pk

    client.force_login(scene.driver)
    assert client.post(completion_url(scene.offer)).status_code == 302
    assert client.post(report_url(scene.booking), {'declared': 'yes'}).status_code == 403
    with pytest.raises(ValidationError) as error:
        ReviewService.create_review(user=scene.other, offer_id=scene.offer.pk,
                                    reviewed_user_id=scene.driver.pk, rating=4)
    assert error.value.code == 'ineligible_booking'


def test_unknown_booking_and_absent_passenger_cannot_submit_report(completed_scene, monkeypatch):
    scene, finished = completed_scene
    freeze(monkeypatch, finished)
    RideBooking.objects.filter(pk=scene.booking.pk).update(no_show_at=finished)
    client = Client()
    client.force_login(scene.passenger)
    unknown = reverse('reviews:report_no_show', kwargs={'booking_id': scene.booking.pk + 1})
    for url in (unknown, report_url(scene.booking)):
        assert client.post(url, {'declared': 'yes'}).status_code == 403
    assert not PenaltyRecord.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_concurrent_report_posts_commit_one_penalty_and_one_projection(completed_scene, monkeypatch):
    assert connection.vendor == 'postgresql'
    scene, finished = completed_scene
    freeze(monkeypatch, finished)
    barrier = Barrier(2, timeout=10)

    def worker():
        db = connections['default']
        try:
            client = Client()
            client.force_login(scene.driver)
            with db.cursor() as cursor:
                cursor.execute('SELECT pg_backend_pid()')
                pid = cursor.fetchone()[0]
            barrier.wait()
            return pid, client.post(report_url(scene.booking), {'declared': 'yes'}).status_code
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: worker(), range(2)))
    assert len({pid for pid, _ in results}) == 2
    assert [status for _, status in results] == [302, 302]
    assert PenaltyRecord.objects.count() == ReputationProfile.objects.count() == 1
    assert not ConductProfile.objects.exists()
