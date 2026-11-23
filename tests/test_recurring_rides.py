"""Feature 009/T035, REQ-011, REQ-003 e REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta, timezone
from importlib import import_module
from threading import Barrier
from zoneinfo import ZoneInfo

import pytest
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, connections, transaction
from django.db.models.deletion import ProtectedError

from reviews.models import ConductProfile
from rides.models import RideOffer, RoutePoint
from rides.services.booking_service import BookingService
from rides.services.cancellation_service import CancellationService

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("recurring_holiday_calendar")]
LOCAL = ZoneInfo('America/Sao_Paulo')


def recurring_model(name):
    return apps.get_model('rides', name)


def rule_data(scene, **changes):
    return dict(driver=scene.driver, origin=scene.points[0], destination=scene.points[-1],
                weekdays=[4, 0, 2], local_time=time(9), seats=2, vehicle_model=' Sedan ',
                vehicle_color=' Azul ', vehicle_plate=' fic1234 ') | changes


def create_rule(scene, **changes):
    return recurring_model('RecurringRideRule').objects.create(**rule_data(scene, **changes))


def test_rule_defaults_and_ordered_stops(cancellation_scene):
    scene = cancellation_scene
    rule = create_rule(scene)
    assert rule.active and rule.timezone == 'America/Sao_Paulo'
    assert rule.weekdays == [0, 2, 4]
    assert (rule.vehicle_model, rule.vehicle_color, rule.vehicle_plate) == ('Sedan', 'Azul', 'FIC1234')
    assert rule.created_at.utcoffset() is not None
    stop = recurring_model('RecurringRideStop')
    assert stop.objects.create(rule=rule, point=scene.points[1], position=1).rule_id == rule.pk


@pytest.mark.parametrize('changes', [
    {'weekdays': []}, {'weekdays': [1, 1]}, {'weekdays': [-1, 7]},
    {'weekdays': [True]}, {'weekdays': [1.5]}, {'weekdays': 'segunda'},
    {'timezone': 'UTC'}, {'local_time': time(9, tzinfo=timezone.utc)}, {'seats': 1.5},
    {'seats': 0}, {'vehicle_plate': ' '},
])
def test_invalid_rule_fields_are_rejected(cancellation_scene, changes):
    with pytest.raises(ValidationError):
        create_rule(cancellation_scene, **changes)


def test_rule_rejects_equal_endpoints_and_ineligible_driver(cancellation_scene):
    scene = cancellation_scene
    with pytest.raises(ValidationError):
        create_rule(scene, destination=scene.points[0])
    with pytest.raises(ValidationError):
        create_rule(scene, driver=scene.passenger)


def test_stop_validation_and_uniqueness_guards_route_history(cancellation_scene):
    scene = cancellation_scene
    rule = create_rule(scene)
    stop = recurring_model('RecurringRideStop')
    for point, position in ((scene.points[0], 1), (scene.points[-1], 1), (scene.points[1], 0),
                            (scene.points[1], 1.5)):
        with pytest.raises(ValidationError):
            stop.objects.create(rule=rule, point=point, position=position)
    stop.objects.create(rule=rule, point=scene.points[1], position=1)
    with pytest.raises(IntegrityError), transaction.atomic():
        stop.objects.bulk_create([stop(rule=rule, point=scene.points[1], position=2)])


@pytest.mark.parametrize('days', [[], [7]])
def test_database_rejects_invalid_weekday_range(cancellation_scene, days):
    model = recurring_model('RecurringRideRule')
    with pytest.raises(IntegrityError), transaction.atomic():
        model.objects.bulk_create([model(**rule_data(cancellation_scene, weekdays=days))])


def test_occurrence_links_actual_date_and_protects_rule_and_offer(cancellation_scene):
    scene = cancellation_scene
    rule = create_rule(scene)
    date = scene.offer.departure_at.astimezone(LOCAL).date()
    model = recurring_model('RecurringRideOccurrence')
    with pytest.raises(ValidationError):
        model.objects.create(rule=rule, local_date=date+timedelta(days=1), offer=scene.offer)
    occurrence = model.objects.create(rule=rule, local_date=date, offer=scene.offer)
    assert occurrence.offer_id == scene.offer.pk
    for item in (rule, scene.offer):
        with pytest.raises(ProtectedError):
            item.delete()
    with pytest.raises(IntegrityError), transaction.atomic():
        model.objects.bulk_create([model(rule=rule, local_date=date, offer=scene.offer)])


@pytest.mark.parametrize('invalid_offer', ['foreign_owner', 'missing'])
def test_occurrence_rejects_foreign_or_missing_offer(cancellation_scene, academic_user_factory, invalid_offer):
    scene = cancellation_scene
    offer_id = scene.offer.pk
    if invalid_offer == 'foreign_owner':
        other = academic_user_factory(role='MOTORISTA', password=None)
        other.academic_status = 'ATIVA'
        other.save(update_fields=['academic_status'])
        rule = create_rule(scene, driver=other)
    else:
        rule = create_rule(scene)
        offer_id += 100
    with pytest.raises(ValidationError) as error:
        recurring_model('RecurringRideOccurrence').objects.create(
            rule=rule, local_date=scene.offer.departure_at.astimezone(LOCAL).date(), offer_id=offer_id,
        )
    assert 'offer' in error.value.message_dict
    assert not rule.occurrences.exists()


def recurring_service():
    return import_module('rides.services.recurring_ride_service')


def generate(rule, at, *, driver=None):
    return recurring_service().RecurringRideService.generate(
        driver=rule.driver if driver is None else driver, rule_id=rule.pk, clock=lambda: at,
    )


def test_horizon_uses_local_calendar_and_includes_both_edges(cancellation_scene):
    # Já é 31/01 em UTC, mas ainda é 30/01 em São Paulo.
    at = datetime(2030, 1, 31, 2, 30, tzinfo=timezone.utc)
    rule = create_rule(cancellation_scene, weekdays=list(range(7)), local_time=time(23, 45))
    first_date = at.astimezone(LOCAL).date()
    last_date = date(2030, 2, 20)  # 05/02 é feriado no calendário de teste.
    expected = tuple(first_date + timedelta(days=offset) for offset in range((last_date - first_date).days + 1))
    first = generate(rule, at)
    repeated = generate(rule, at)
    assert first.created_dates == expected and not first.existing_dates
    assert repeated.existing_dates == expected and not repeated.created_dates
    assert {item.offer.departure_at.astimezone(LOCAL).time() for item in rule.occurrences.all()} == {time(23, 45)}
    assert rule.occurrences.count() == 22


@pytest.mark.parametrize('at_minute', [0, 1])
def test_selected_weekdays_include_weekends_and_skip_today_at_or_after_departure(cancellation_scene, at_minute):
    at = datetime(2030, 1, 4, 12, at_minute, tzinfo=timezone.utc)
    local_day = at.astimezone(LOCAL).date()
    selected = [local_day.weekday(), 5, 6]
    rule = create_rule(cancellation_scene, weekdays=selected, local_time=time(9))
    expected = tuple(
        local_day + timedelta(days=offset) for offset in range(1, 21)
        if (local_day + timedelta(days=offset)).weekday() in selected
    )
    assert generate(rule, at).created_dates == expected
    assert any(day.weekday() >= 5 for day in expected)


def test_rule_edits_and_deactivation_preserve_snapshots(cancellation_scene):
    scene = cancellation_scene
    rule = create_rule(scene, weekdays=[0], seats=2)
    other_stop = RoutePoint.objects.create(code='recurring-extra', name='Parada adicional sintética')
    stop = recurring_model('RecurringRideStop')
    stop.objects.create(rule=rule, point=other_stop, position=2)
    stop.objects.create(rule=rule, point=scene.points[1], position=1)

    at = scene.departure
    result = generate(rule, at)
    original = rule.occurrences.order_by('local_date').first().offer
    assert original.seats == 2 and original.vehicle_model == 'Sedan'
    assert list(original.waypoints.values_list('point_id', flat=True)) == [scene.points[1].pk, other_stop.pk]
    rule.seats = 3
    rule.vehicle_model = 'Hatch'
    rule.save()
    stop.objects.filter(rule=rule, point=other_stop).delete()
    future = generate(rule, at + timedelta(days=7))
    assert future.created_dates and future.existing_dates
    for item in rule.occurrences.exclude(local_date__in=result.created_dates):
        assert item.offer.seats == 3 and item.offer.vehicle_model == 'Hatch'
        assert list(item.offer.waypoints.values_list('point_id', flat=True)) == [scene.points[1].pk]
    original.refresh_from_db()
    assert original.seats == 2 and original.vehicle_model == 'Sedan'
    assert list(original.waypoints.values_list('point_id', flat=True)) == [scene.points[1].pk, other_stop.pk]

    rule.active = False
    rule.save()
    count = rule.occurrences.count()
    assert not generate(rule, at + timedelta(days=28)).created_dates
    assert rule.occurrences.count() == count


@pytest.mark.parametrize('reason', ['other', 'disabled', 'pending', 'suspended'])
def test_revalidates_owner_and_conduct_for_every_generation(cancellation_scene, reason):
    scene = cancellation_scene
    rule = create_rule(scene)
    driver = scene.driver
    at = scene.departure
    if reason == 'other':
        driver = scene.passenger
    elif reason == 'suspended':
        ConductProfile.objects.create(user=driver, suspended_until=at + timedelta(days=14))
    else:
        update = {'is_active': False} if reason == 'disabled' else {'academic_status': 'PENDENTE'}
        type(driver).objects.filter(pk=driver.pk).update(**update)
    with pytest.raises(PermissionDenied):
        generate(rule, at, driver=driver)
    assert not rule.occurrences.exists()
    assert RideOffer.objects.count() == 1


@pytest.mark.parametrize('invalid', [datetime(2030, 1, 1), '2030-01-01'])
def test_generator_requires_an_aware_reference(cancellation_scene, invalid):
    rule = create_rule(cancellation_scene)
    with pytest.raises(ValidationError):
        generate(rule, invalid)
    assert not rule.occurrences.exists()


def test_intermediate_publication_failure_rolls_back_entire_batch(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    rule = create_rule(scene, weekdays=list(range(7)))
    module = recurring_service()
    publish = module.publish_offer
    calls = []

    def fail_second(**kwargs):
        offer = publish(**kwargs)
        calls.append(offer.pk)
        if len(calls) == 2:
            raise RuntimeError('falha sintética')
        return offer

    with monkeypatch.context() as patch:
        patch.setattr(module, 'publish_offer', fail_second)
        with pytest.raises(RuntimeError, match='falha sintética'):
            generate(rule, scene.departure)
    assert len(calls) == 2 and not rule.occurrences.exists()
    assert RideOffer.objects.count() == 1
    assert generate(rule, scene.departure).created_dates


@pytest.mark.django_db(transaction=True)
def test_concurrent_generation_serializes_rule_across_postgresql_connections(cancellation_scene):
    assert connection.vendor == 'postgresql'
    scene = cancellation_scene
    rule = create_rule(scene, weekdays=[0])
    barrier = Barrier(2, timeout=10)

    def worker():
        db = connections['default']
        try:
            with transaction.atomic(), db.cursor() as cursor:
                cursor.execute("SET LOCAL lock_timeout = '10s'")
                cursor.execute('SELECT pg_backend_pid()')
                pid = cursor.fetchone()[0]
                barrier.wait()
                return pid, generate(rule, scene.departure)
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        first, second = [worker.result(timeout=20) for worker in (pool.submit(worker), pool.submit(worker))]
    assert first[0] != second[0]
    results = sorted((first[1], second[1]), key=lambda item: len(item.created_dates))
    assert not results[0].created_dates and not results[1].existing_dates
    assert results[0].existing_dates == results[1].created_dates
    assert rule.occurrences.count() == len(results[1].created_dates)


def test_generator_rejects_anonymous_driver_and_invalid_rule_identifier(cancellation_scene):
    rule = create_rule(cancellation_scene)
    with pytest.raises(PermissionDenied):
        generate(rule, cancellation_scene.departure, driver=AnonymousUser())
    with pytest.raises(ValidationError):
        recurring_service().RecurringRideService.generate(rule_id=True, driver=rule.driver)
    assert not rule.occurrences.exists()


def test_cancelling_one_occurrence_keeps_others_and_regeneration_does_not_replace_it(cancellation_scene):
    scene = cancellation_scene
    rule = create_rule(scene, weekdays=[0])
    reference = scene.departure
    result = generate(rule, reference)
    cancelled, preserved = rule.occurrences.order_by('local_date')[:2]

    def reserve(occurrence):
        return BookingService.create_booking(
            passenger=scene.passenger, offer_id=occurrence.offer_id,
            boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk,
        )

    cancelled_booking = reserve(cancelled)
    reserve(preserved)
    other_offers = RideOffer.objects.filter(recurring_occurrence__rule=rule).exclude(pk=cancelled.offer_id)
    initial_others = list(other_offers.order_by('pk').values())
    initial_bookings = list(preserved.offer.bookings.values())
    initial_rule = type(rule).objects.values().get(pk=rule.pk)

    CancellationService.cancel_offer(user=scene.driver, offer_id=cancelled.offer_id, clock=lambda: reference)
    replay = generate(rule, reference)

    assert not replay.created_dates and replay.existing_dates == result.created_dates
    assert rule.occurrences.count() == len(result.created_dates)
    assert rule.occurrences.get(local_date=cancelled.local_date).offer_id == cancelled.offer_id
    cancelled.offer.refresh_from_db()
    cancelled_booking.refresh_from_db()
    assert cancelled.offer.status == RideOffer.Status.CANCELADA
    assert cancelled_booking.status == cancelled_booking.Status.CANCELADA
    assert list(other_offers.order_by('pk').values()) == initial_others
    assert list(preserved.offer.bookings.values()) == initial_bookings
    assert type(rule).objects.values().get(pk=rule.pk) == initial_rule
