"""Calendário da Feature 009/T008, com o contrato HTTP simulado."""
import json
from datetime import date
from io import BytesIO
from urllib.error import URLError

import pytest

from rides.services import holiday_calendar


def test_horizon_crosses_year_and_reuses_cached_calendars(monkeypatch, settings):
    settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                                  'LOCATION': 'holiday-calendar-year-boundary'}}
    returned = {
        2030: ['2030-12-25', '2030-12-28'],
        2031: ['2031-01-01'],
    }
    calls = []

    def response(request, *, timeout):
        assert request.get_header('Accept') == 'application/json'
        assert request.get_header('User-agent') == 'CaronaUniville/1.0'
        calls.append((request.full_url, timeout))
        year = int(request.full_url.rsplit('/', 1)[-1].split('?')[0])
        return BytesIO(json.dumps([{'date': day} for day in returned[year]]).encode())

    monkeypatch.setattr(holiday_calendar, 'urlopen', response)
    for _ in range(2):
        assert holiday_calendar.recurrence_end_date(date(2030, 12, 23)) == date(2031, 1, 14)
    assert calls == [
        ('https://brasilapi.com.br/api/feriados/v1/2030?uf=SC', 5),
        ('https://brasilapi.com.br/api/feriados/v1/2031?uf=SC', 5),
    ]


@pytest.mark.parametrize('body', [None, b'invalid json', b'[]', b'{}', b'[{}]', b'[{"date":"2030-12-25"}]'])
def test_failed_calendar_is_rejected_and_can_be_retried(monkeypatch, settings, body):
    settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                                  'LOCATION': 'holiday-calendar-retry'}}
    holiday_calendar.cache.clear()

    def invalid_response(request, *, timeout):
        if body is None:
            raise URLError('conexão indisponível')
        return BytesIO(body)

    monkeypatch.setattr(holiday_calendar, 'urlopen', invalid_response)
    with pytest.raises(holiday_calendar.HolidayCalendarUnavailable):
        holiday_calendar.holiday_dates(2031)
    monkeypatch.setattr(
        holiday_calendar, 'urlopen',
        lambda request, timeout: BytesIO(b'[{"date":"2031-01-01"}]'),
    )
    assert holiday_calendar.holiday_dates(2031) == {date(2031, 1, 1)}
