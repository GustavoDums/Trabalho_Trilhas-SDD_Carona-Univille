"""Calendário público usado para calcular o limite das caronas recorrentes."""
import json
from datetime import date, timedelta
from http.client import HTTPException
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.core.exceptions import ValidationError

HORIZON_BUSINESS_DAYS = 15
HOLIDAY_CACHE_TIMEOUT = 24 * 60 * 60


class HolidayCalendarUnavailable(ValidationError):
    def __init__(self):
        super().__init__(
            "O calendário de feriados está indisponível. Tente gerar as caronas novamente mais tarde.",
            code="holiday_calendar_unavailable",
        )


def holiday_dates(year):
    key = f"recurring-holiday-calendar:brasilapi:SC:{year}"
    cached_dates = cache.get(key)
    if cached_dates is not None:
        return cached_dates

    request = Request(
        f"https://brasilapi.com.br/api/feriados/v1/{year}?uf=SC",
        headers={"Accept": "application/json", "User-Agent": "CaronaUniville/1.0"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.load(response)
        if not isinstance(payload, list) or not payload:
            raise ValueError("Calendário anual vazio ou inválido.")
        dates = frozenset(date.fromisoformat(item["date"]) for item in payload)
        if any(day.year != year for day in dates):
            raise ValueError("Data de feriado fora do ano consultado.")
    except (OSError, HTTPException, ValueError, TypeError, KeyError) as error:
        raise HolidayCalendarUnavailable() from error

    cache.set(key, dates, timeout=HOLIDAY_CACHE_TIMEOUT)
    return dates


def recurrence_end_date(first_date):
    """Retorna o 15º dia útil a partir da data local, com contagem inclusiva."""
    current = first_date
    year = current.year
    holidays = holiday_dates(year)
    remaining = HORIZON_BUSINESS_DAYS
    while True:
        if current.weekday() < 5 and current not in holidays:
            remaining -= 1
            if remaining == 0:
                return current
        current += timedelta(days=1)
        if current.year != year:
            year = current.year
            holidays = holiday_dates(year)
