"""Fluxos da Feature 008, REQ-010, REQ-003 e REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from threading import Barrier

import pytest
from django.db import connection, connections
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from reviews.models import ConductProfile, PenaltyRecord, ReputationProfile
from reviews.services.penalty_service import PenaltyService
from reviews.services.review_service import ReviewService
from rides.models import RideBooking, RideOffer
from rides.services.booking_service import BookingService
from rides.services.cancellation_service import CancellationService
from rides.services.offers import publish_offer

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


def offer_data(scene):
    return dict(origin=scene.points[0], destination=scene.points[-1], departure_at=scene.departure,
                seats=2, vehicle_model='Veículo Sintético', vehicle_color='Azul', vehicle_plate='FICTICIO')


def blocked_action(scene, role):
    if role == 'driver':
        data = offer_data(scene)
        return reverse('rides:offer-create'), dict(
            data, origin=data['origin'].pk, destination=data['destination'].pk,
            departure_at=timezone.localtime(scene.departure).strftime('%Y-%m-%dT%H:%M'),
            **{'waypoints-TOTAL_FORMS': '0', 'waypoints-INITIAL_FORMS': '0'},
        )
    return reverse('rides:book', kwargs={'offer_id': scene.offer.pk}), {
        'boarding_point_id': scene.points[0].pk, 'alighting_point_id': scene.points[-1].pk,
    }


@pytest.mark.parametrize('role', ['driver', 'other'])
def test_suspension_blocks_http_actions_and_expires_at_exact_instant(cancellation_scene, monkeypatch, role):
    scene = cancellation_scene
    RideOffer.objects.filter(pk=scene.offer.pk).update(seats=2)
    actor = getattr(scene, role)
    until = scene.departure - timedelta(days=1)
    ConductProfile.objects.create(user=actor, suspended_until=until)
    freeze(monkeypatch, until - timedelta(seconds=1))
    client = Client()
    client.force_login(actor)
    path, data = blocked_action(scene, role)
    if role == 'driver':
        assert client.get(path).status_code == 403
    else:
        assert client.get(path).status_code == 405
    denied = client.post(path, data)
    assert denied.status_code == 403
    assert 'Suspensão disciplinar' in denied.content.decode()
    assert RideOffer.objects.count() == RideBooking.objects.count() == 1
    actor.refresh_from_db()
    assert actor.academic_status == 'ATIVA' and actor.is_active

    freeze(monkeypatch, until)
    if role == 'driver':
        assert client.get(path).status_code == 200
    assert client.post(path, data).status_code == 302


@pytest.mark.parametrize('role', ['driver', 'other'])
def test_service_rejects_suspended_actor_using_current_database_state(cancellation_scene, monkeypatch, role):
    scene = cancellation_scene
    RideOffer.objects.filter(pk=scene.offer.pk).update(seats=2)
    actor = getattr(scene, role)
    until = scene.departure - timedelta(days=1)
    freeze(monkeypatch, until - timedelta(seconds=1))
    assert not ConductProfile.objects.filter(user=actor).exists()
    ConductProfile.objects.create(user=actor, suspended_until=until)

    def write():
        if role == 'driver':
            return publish_offer(driver=actor, data=offer_data(scene), points=[])
        return BookingService.create_booking(
            passenger=actor, offer_id=scene.offer.pk,
            boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk,
        )

    with pytest.raises(PermissionDenied, match='Suspensão disciplinar'):
        write()
    assert RideOffer.objects.count() == RideBooking.objects.count() == 1
    freeze(monkeypatch, until)
    assert write().pk


@pytest.mark.parametrize('role', ['driver', 'passenger'])
def test_suspended_account_can_login_read_and_cancel_existing_commitment(cancellation_scene, monkeypatch, role):
    scene = cancellation_scene
    actor = getattr(scene, role)
    now = scene.departure - timedelta(hours=5)
    freeze(monkeypatch, now)
    actor.set_password('Senha-sintetica-T034!')
    actor.save(update_fields=['password'])
    ConductProfile.objects.create(user=actor, suspended_until=now + timedelta(days=14))
    client = Client(enforce_csrf_checks=True)
    login = reverse('accounts:login')
    assert client.get(login).status_code == 200
    assert client.post(login, {'email': actor.email, 'password': 'Senha-sintetica-T034!',
                              'csrfmiddlewaretoken': client.cookies['csrftoken'].value}).status_code == 302
    assert client.get(reverse('accounts:profile')).status_code == 200
    assert client.get(reverse('accounts:activation')).status_code == 302
    assert client.get(reverse('rides:my_bookings')).status_code == 200
    if role == 'driver':
        assert client.get(reverse('rides:my-offers')).status_code == 200
        url = reverse('rides:cancel_offer', kwargs={'offer_id': scene.offer.pk})
    else:
        assert client.get(reverse('rides:search')).status_code == 200
        url = reverse('rides:cancel_booking', kwargs={'booking_id': scene.booking.pk})
    assert client.post(url, {'csrfmiddlewaretoken': client.cookies['csrftoken'].value}).status_code == 302
    scene.booking.refresh_from_db()
    assert scene.booking.status == RideBooking.Status.CANCELADA
    logout = reverse('accounts:logout')
    assert client.get(logout).status_code == 405
    assert client.post(logout).status_code == 403
    assert client.post(logout, {'csrfmiddlewaretoken': client.cookies['csrftoken'].value}).url == login
    assert client.get(reverse('accounts:profile')).status_code == 302


def test_third_report_immediately_blocks_new_booking(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    occurrence = scene.departure + timedelta(minutes=10)
    for days in (1, 2):
        old_offer = publish_offer(
            driver=scene.driver, data=dict(offer_data(scene), departure_at=scene.departure-timedelta(days=days)),
            points=[],
        )
        old_booking = RideBooking.objects.create(
            offer=old_offer, passenger=scene.passenger,
            boarding_point=scene.points[0], alighting_point=scene.points[-1],
        )
        at = occurrence - timedelta(days=days)
        PenaltyRecord.objects.create(
            subject=scene.passenger, actor=scene.driver, offer=old_offer, booking=old_booking,
            kind=PenaltyRecord.Kind.NO_SHOW, source_key=f'no-show:{old_offer.pk}:{scene.passenger.pk}',
            occurred_at=at, reported_at=at, delta=Decimal('-0.50'),
        )
    finished = occurrence + timedelta(minutes=1)
    new_offer = publish_offer(
        driver=scene.driver, data=dict(offer_data(scene), departure_at=scene.departure + timedelta(days=15)), points=[],
    )
    ReviewService.complete_offer(user=scene.driver, offer_id=scene.offer.pk, clock=lambda: finished)
    freeze(monkeypatch, finished)
    reporter = Client()
    reporter.force_login(scene.driver)
    assert reporter.post(report_url(scene.booking), {'declared': 'yes'}).status_code == 302
    assert ConductProfile.objects.get(user=scene.passenger).suspended_until == occurrence + timedelta(days=14)

    passenger = Client()
    passenger.force_login(scene.passenger)
    url = reverse('rides:book', kwargs={'offer_id': new_offer.pk})
    data = {'boarding_point_id': scene.points[0].pk, 'alighting_point_id': scene.points[-1].pk}
    assert passenger.post(url, data).status_code == 403
    assert not RideBooking.objects.filter(offer=new_offer).exists()


def test_history_is_discoverable_and_only_renders_own_occurrences(completed_scene, monkeypatch):
    scene, now = completed_scene
    PenaltyService.report_no_show(user=scene.driver, booking_id=scene.booking.pk,
                                 declared=True, clock=lambda: now)
    foreign_offer = publish_offer(
        driver=scene.driver, data=dict(offer_data(scene), departure_at=scene.departure + timedelta(hours=1)),
        points=[],
    )
    CancellationService.cancel_offer(user=scene.driver, offer_id=foreign_offer.pk, clock=lambda: now)
    until = now + timedelta(days=14)
    ConductProfile.objects.create(user=scene.passenger, suspended_until=until)
    freeze(monkeypatch, now)
    client = Client()
    client.force_login(scene.passenger)
    url = '/conta/conduta/'

    assert url.encode() in client.get(reverse('accounts:profile')).content
    action, data = blocked_action(scene, 'other')
    denied = client.post(action, data)
    assert denied.status_code == 403 and url.encode() in denied.content

    history = client.get(url, {'user_id': scene.driver.pk})
    assert history.status_code == 200
    assert 'no-store' in history.headers['Cache-Control']
    html = history.content.decode()
    assert 'Não comparecimento' in html and 'Cancelamento tardio' not in html
    assert 'Suspensão disciplinar em vigor até' in html and '0,50' in html
    assert timezone.localtime(until).strftime('%d/%m/%Y %H:%M:%S') in html
    for secret in (scene.driver.email, scene.driver.full_name, scene.offer.vehicle_plate):
        assert secret not in html

    client.force_login(scene.driver)
    response = client.get(url, {'subject_id': scene.passenger.pk, 'user_id': scene.passenger.pk})
    assert response.status_code == 200
    html = response.content.decode()
    assert 'Cancelamento tardio' in html and 'Não comparecimento' not in html
    assert 'Suspensão disciplinar em vigor até' not in html
    assert '0,20' in html


def test_empty_history_stays_private_and_only_allows_reads(cancellation_scene, pending_user, monkeypatch):
    scene = cancellation_scene
    freeze(monkeypatch, scene.departure)
    url = '/conta/conduta/'
    client = Client()
    assert client.get(url).url.startswith('/accounts/login/')
    client.force_login(pending_user)
    assert client.get(url).url == reverse('accounts:activation')
    client.force_login(scene.other)
    response = client.get(url)
    assert response.status_code == 200
    assert 'Nenhuma ocorrência registrada' in response.content.decode()
    assert client.post(url, {'user_id': scene.driver.pk}).status_code == 405
    assert client.get(url + str(scene.driver.pk) + '/').status_code == 404
    assert not PenaltyRecord.objects.exists()


def test_history_displays_expired_suspension_at_boundary(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    until = scene.departure
    ConductProfile.objects.create(user=scene.passenger, suspended_until=until)
    client = Client()
    freeze(monkeypatch, until - timedelta(seconds=1))
    client.force_login(scene.passenger)
    url = '/conta/conduta/'
    assert 'Suspensão disciplinar em vigor até' in client.get(url).content.decode()

    freeze(monkeypatch, until)
    history = client.get(url)
    assert history.status_code == 200
    assert 'Última suspensão encerrada em' in history.content.decode()
    scene.passenger.refresh_from_db()
    assert scene.passenger.academic_status == 'ATIVA' and scene.passenger.is_active
