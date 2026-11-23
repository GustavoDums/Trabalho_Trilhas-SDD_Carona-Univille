"""Feature 009/T036, REQ-011, REQ-003 e REQ-017."""
from datetime import date, time, timedelta
from io import StringIO
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from reviews.models import ConductProfile
from rides.models import RecurringRideRule, RecurringRideStop, RideBooking, RideOffer
from rides.services import holiday_calendar, recurring_ride_service

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("recurring_holiday_calendar")]
LOCAL = ZoneInfo('America/Sao_Paulo')
RECURRING_URL = '/caronas/recorrentes/'


@pytest.fixture
def flow(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    at = scene.departure - timedelta(hours=2)
    monkeypatch.setattr('django.utils.timezone.now', lambda: at)
    return scene, at


def rule_payload(scene):
    return {
        'origin': scene.points[0].pk, 'destination': scene.points[-1].pk,
        'weekdays': ['0', '4', '6'], 'local_time': '09:00', 'seats': '2',
        'vehicle_model': 'Veículo recorrente sintético', 'vehicle_color': 'Azul', 'vehicle_plate': 'SEGREDO035',
        'waypoints-TOTAL_FORMS': '1', 'waypoints-INITIAL_FORMS': '0',
        'waypoints-0-point': scene.points[1].pk,
    }


def test_driver_creates_rule_with_csrf_and_sees_generated_dates(flow):
    scene, at = flow
    client = Client(enforce_csrf_checks=True)
    client.force_login(scene.driver)
    assert RECURRING_URL.encode() in client.get(reverse('rides:my-offers')).content
    form = client.get(RECURRING_URL)
    assert form.status_code == 200 and 'csrfmiddlewaretoken' in form.content.decode()
    assert not RecurringRideRule.objects.exists()
    data = dict(rule_payload(scene), driver=scene.passenger.pk, active='false', timezone='UTC',
                csrfmiddlewaretoken=client.cookies['csrftoken'].value)
    response = client.post(RECURRING_URL, data, follow=True)
    assert response.redirect_chain == [(RECURRING_URL, 302)]
    rule = RecurringRideRule.objects.get(driver=scene.driver)
    assert rule.active and rule.timezone == 'America/Sao_Paulo'
    expected = [at.astimezone(LOCAL).date() + timedelta(days=n) for n in range(21)
                if (at.astimezone(LOCAL).date() + timedelta(days=n)).weekday() in (0, 4, 6)]
    assert list(rule.occurrences.order_by('local_date').values_list('local_date', flat=True)) == expected
    for occurrence in rule.occurrences.all():
        assert list(occurrence.offer.waypoints.values_list('point_id', flat=True)) == [scene.points[1].pk]
    html = response.content.decode()
    assert '15º dia útil' in html
    assert 'Datas geradas' in html and expected[-1].strftime('%d/%m/%Y') in html
    assert data['vehicle_plate'] not in html and scene.driver.email not in html


@pytest.mark.parametrize('issue,expected', [
    ('visitor', 302), ('pending', 302), ('passenger', 403), ('csrf', 403),
    ('suspended', 403), ('weekday', 400), ('stop', 400), ('endpoints', 400), ('controls', 400),
])
def test_invalid_or_unauthorized_request_creates_no_rule_or_offer(flow, pending_user, issue, expected):
    scene, at = flow
    client = Client(enforce_csrf_checks=issue == 'csrf')
    if issue != 'visitor':
        user = {'pending': pending_user, 'passenger': scene.passenger}.get(issue, scene.driver)
        client.force_login(user)
    data = rule_payload(scene)
    if issue == 'weekday':
        data['weekdays'] = ['7']
    elif issue == 'stop':
        data['waypoints-0-point'] = scene.points[0].pk
    elif issue == 'endpoints':
        data['destination'] = scene.points[0].pk
    elif issue == 'controls':
        data['waypoints-INITIAL_FORMS'] = '1'
    elif issue == 'suspended':
        ConductProfile.objects.create(user=scene.driver, suspended_until=at + timedelta(days=1))
        assert client.get(RECURRING_URL).status_code == 200

    response = client.post(RECURRING_URL, data)
    assert response.status_code == expected
    assert not RecurringRideRule.objects.exists() and RideOffer.objects.count() == 1
    assert data['vehicle_plate'].encode() not in response.content


def test_listing_uses_session_and_never_generates_on_get(flow, academic_user_factory):
    scene, _ = flow
    client = Client()
    client.force_login(scene.driver)
    assert client.post(RECURRING_URL, rule_payload(scene)).status_code == 302
    rule = RecurringRideRule.objects.get(driver=scene.driver)
    other = academic_user_factory(role='MOTORISTA', password=None)
    other.academic_status = 'ATIVA'
    other.save(update_fields=['academic_status'])
    client.force_login(other)
    before = RideOffer.objects.count()

    response = client.get(RECURRING_URL, {'driver_id': scene.driver.pk, 'rule_id': rule.pk})
    assert response.status_code == 200
    text = response.content.decode()
    assert 'Nenhuma regra cadastrada' in text
    assert 'Datas geradas' not in text
    assert rule.vehicle_plate not in text and scene.driver.email not in text
    assert RideOffer.objects.count() == before


def test_generation_error_rolls_back_rule_stops_and_offers(flow, monkeypatch):
    scene, _ = flow
    original = recurring_ride_service.publish_offer

    def fail_after_save(**kwargs):
        original(**kwargs)
        raise ValidationError('SEGREDO035')

    monkeypatch.setattr(recurring_ride_service, 'publish_offer', fail_after_save)
    client = Client()
    client.force_login(scene.driver)
    response = client.post(RECURRING_URL, rule_payload(scene))
    assert response.status_code == 400 and 'SEGREDO035' not in response.content.decode()
    assert not RecurringRideRule.objects.exists() and RideOffer.objects.count() == 1


def new_driver(factory):
    driver = factory(role='MOTORISTA', password=None)
    driver.academic_status = 'ATIVA'
    driver.save(update_fields=['academic_status'])
    return driver


def create_command_rule(scene, *, driver=None, active=True):
    rule = RecurringRideRule.objects.create(
        driver=driver or scene.driver, origin=scene.points[0], destination=scene.points[-1],
        weekdays=[0, 4, 6], local_time=time(9), seats=2, active=active,
        vehicle_model='Veículo recorrente sintético', vehicle_color='Azul', vehicle_plate='SEGREDO035',
    )
    RecurringRideStop.objects.create(rule=rule, point=scene.points[1], position=1)
    return rule


def dates_of(rule):
    return tuple(rule.occurrences.order_by('local_date').values_list('local_date', flat=True))


def test_listing_fetches_own_rules_and_dates_without_per_rule_queries(flow):
    scene, _ = flow
    client = Client()
    client.force_login(scene.driver)
    data = rule_payload(scene)
    assert client.post(RECURRING_URL, data).status_code == 302
    with CaptureQueriesContext(connection) as first:
        assert client.get(RECURRING_URL).status_code == 200
    assert client.post(RECURRING_URL, dict(data, local_time='10:00')).status_code == 302
    with CaptureQueriesContext(connection) as both:
        response = client.get(RECURRING_URL)
    assert len(both) == len(first)
    assert response.content.count(b'Datas geradas') == 2


def test_command_and_form_agree_and_daily_rerun_completes_horizon(flow, academic_user_factory, monkeypatch):
    scene, at = flow
    client = Client()
    client.force_login(scene.driver)
    assert client.post(RECURRING_URL, rule_payload(scene)).status_code == 302
    form_rule = RecurringRideRule.objects.get(driver=scene.driver)
    driver = new_driver(academic_user_factory)
    rule = create_command_rule(scene, driver=driver)
    output = StringIO()
    call_command('generate_recurring_rides', '--rule', str(rule.pk), stdout=output)

    dates = dates_of(rule)
    assert dates == dates_of(form_rule)
    assert 'criadas=' in output.getvalue()
    assert all(day.isoformat() in output.getvalue() for day in dates)
    assert rule.vehicle_plate not in output.getvalue() and driver.email not in output.getvalue()
    original = dict(rule.occurrences.values_list('local_date', 'offer_id'))

    repeated = StringIO()
    call_command('generate_recurring_rides', '--rule', str(rule.pk), stdout=repeated)
    assert 'criadas=-' in repeated.getvalue() and 'existentes=' in repeated.getvalue()
    assert dict(rule.occurrences.values_list('local_date', 'offer_id')) == original

    later = at + timedelta(days=1)
    monkeypatch.setattr('django.utils.timezone.now', lambda: later)
    call_command('generate_recurring_rides', '--rule', str(rule.pk), stdout=StringIO())
    new_day = date(2030, 1, 25)
    assert dates_of(rule) == (*dates, new_day)
    assert all(rule.occurrences.get(local_date=day).offer_id == pk for day, pk in original.items())


def test_daily_all_skips_inactive_rules_and_revalidates_driver(flow, academic_user_factory):
    scene, at = flow
    suspended = new_driver(academic_user_factory)
    eligible_rule = create_command_rule(scene)
    disabled_rule = create_command_rule(scene, active=False)
    suspended_rule = create_command_rule(scene, driver=suspended)
    ConductProfile.objects.create(user=suspended, suspended_until=at + timedelta(days=1))
    output = StringIO()
    call_command('generate_recurring_rides', '--all', stdout=output)
    assert eligible_rule.occurrences.exists()
    assert not disabled_rule.occurrences.exists() and not suspended_rule.occurrences.exists()
    assert f'regra={suspended_rule.pk} ignorada' in output.getvalue()
    assert f'regra={disabled_rule.pk} ' not in output.getvalue()
    assert suspended.email not in output.getvalue()


def test_calendar_outage_rejects_generation_and_keeps_existing_occurrences(flow, client, monkeypatch):
    scene, _ = flow
    client.force_login(scene.driver)
    assert client.post(RECURRING_URL, rule_payload(scene)).status_code == 302
    rule = RecurringRideRule.objects.get(driver=scene.driver)
    before = dict(rule.occurrences.values_list('local_date', 'offer_id'))

    def unavailable(year):
        raise holiday_calendar.HolidayCalendarUnavailable()

    monkeypatch.setattr(holiday_calendar, 'holiday_dates', unavailable)
    response = client.get(RECURRING_URL)
    assert response.status_code == 200
    assert 'Exibindo as caronas já geradas' in response.content.decode()
    assert 'Datas geradas' in response.content.decode()

    response = client.post(RECURRING_URL, rule_payload(scene))
    assert response.status_code == 503 and 'calendário de feriados está indisponível' in response.content.decode()
    assert RecurringRideRule.objects.count() == 1
    with pytest.raises(CommandError, match='calendário de feriados está indisponível'):
        call_command('generate_recurring_rides', '--all', stdout=StringIO())
    assert dict(rule.occurrences.values_list('local_date', 'offer_id')) == before


@pytest.mark.parametrize('options', [(), ('--rule', '0'), ('--rule', '999999'), ('--rule', '1', '--all')])
def test_command_requires_valid_explicit_selection(flow, options):
    with pytest.raises(CommandError):
        call_command('generate_recurring_rides', *options, stdout=StringIO(), stderr=StringIO())
    assert RideOffer.objects.count() == 1


def test_command_reports_sanitized_error_and_rolls_back_only_failed_rule(flow, academic_user_factory, monkeypatch):
    scene, _ = flow
    failed = create_command_rule(scene)
    good = create_command_rule(scene, driver=new_driver(academic_user_factory))
    original = recurring_ride_service.publish_offer

    def fail_after_save(**kwargs):
        offer = original(**kwargs)
        if offer.driver_id == scene.driver.pk:
            raise ValidationError(f'Erro sintético: {scene.driver.email} SEGREDO035')
        return offer

    monkeypatch.setattr(recurring_ride_service, 'publish_offer', fail_after_save)
    stdout, stderr = StringIO(), StringIO()
    with pytest.raises(CommandError, match='Falha na geração'):
        call_command('generate_recurring_rides', '--all', stdout=stdout, stderr=stderr)
    assert not failed.occurrences.exists()
    assert good.occurrences.exists()
    assert RideOffer.objects.filter(driver=scene.driver).count() == 1
    output = stdout.getvalue() + stderr.getvalue()
    assert f'regra={failed.pk} falhou' in output
    assert scene.driver.email not in output and failed.vehicle_plate not in output


def test_command_generated_ride_appears_in_search_and_accepts_booking(flow):
    scene, _ = flow
    rule = create_command_rule(scene)
    call_command('generate_recurring_rides', '--rule', str(rule.pk), stdout=StringIO())
    offer = rule.occurrences.order_by('local_date').first().offer
    client = Client()
    client.force_login(scene.other)
    response = client.get(reverse('rides:search'), {
        'boarding_id': scene.points[1].pk, 'alighting_id': scene.points[-1].pk,
        'desired_at': offer.departure_at.astimezone(LOCAL).isoformat(),
    })
    assert response.status_code == 200
    assert f'data-offer-id="{offer.pk}"' in response.content.decode()
    assert rule.vehicle_plate.encode() not in response.content
    result = client.post(reverse('rides:book', kwargs={'offer_id': offer.pk}), {
        'boarding_point_id': scene.points[1].pk, 'alighting_point_id': scene.points[-1].pk,
    })
    assert result.status_code == 302
    booking = RideBooking.objects.get(offer=offer)
    assert booking.passenger_id == scene.other.pk and booking.status == RideBooking.Status.CONFIRMADA
