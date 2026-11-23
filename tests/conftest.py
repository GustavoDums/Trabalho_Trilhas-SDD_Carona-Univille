"""Fixtures compartilhadas da Feature 001 / T003, apenas com dados sintéticos."""

import itertools
import json

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.fixture
def academic_whitelist():
    path = settings.BASE_DIR / "accounts" / "fixtures" / "academic_whitelist.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def academic_user_factory(db):
    sequence = itertools.count(1)

    def create_user(**overrides):
        values = {
            "email": f"usuario.sintetico{next(sequence)}@univille.br",
            "full_name": "Usuário Sintético",
            "role": "PASSAGEIRO",
            "password": "Senha-sintetica-2026!",
        }
        values.update(overrides)
        return get_user_model().objects.create_user(**values)

    return create_user


@pytest.fixture
def pending_user(academic_user_factory):
    return academic_user_factory()


@pytest.fixture
def active_user(academic_user_factory):
    user = academic_user_factory()
    user.academic_status = "ATIVA"
    user.save(update_fields=["academic_status", "updated_at"])
    return user


@pytest.fixture
def pending_client(pending_user):
    client = Client()
    client.force_login(pending_user)
    return client


@pytest.fixture
def active_client(active_user):
    client = Client()
    client.force_login(active_user)
    return client


@pytest.fixture
def recurring_holiday_calendar(monkeypatch):
    """Calendário sintético estável para os testes de recorrência no PostgreSQL."""
    from datetime import date

    def dates(year):
        return frozenset({date(year, 1, 1), date(year, 2, 5), date(year, 12, 25)})

    monkeypatch.setattr("rides.services.holiday_calendar.holiday_dates", dates)


@pytest.fixture
def cancellation_scene(academic_user_factory):
    """Dados próprios para testes transacionais, sem depender de seeds após flush."""
    from datetime import datetime, timezone as dt_timezone
    from types import SimpleNamespace
    from rides.models import RideOffer, RoutePoint, Waypoint
    from rides.services.booking_service import BookingService
    users = [academic_user_factory(role=role, password=None)
             for role in ("MOTORISTA", "PASSAGEIRO", "PASSAGEIRO")]
    for user in users:
        user.academic_status = "ATIVA"
        user.save(update_fields=["academic_status", "updated_at"])
    points = [RoutePoint.objects.get_or_create(code=code, defaults={"name": name})[0]
              for code, name in (("cancel-origin", "Origem Sintética"),
                                 ("cancel-stop", "Parada Sintética"),
                                 ("cancel-destination", "Destino Sintético"))]
    departure = datetime(2030, 1, 4, 12, tzinfo=dt_timezone.utc)
    offer = RideOffer.objects.create(
        driver=users[0], origin=points[0], destination=points[-1], departure_at=departure,
        seats=1, vehicle_model="Veículo Sintético", vehicle_color="Azul", vehicle_plate="PRIVADA")
    Waypoint.objects.create(offer=offer, point=points[1], position=1)
    booking = BookingService.create_booking(
        passenger=users[1], offer_id=offer.pk,
        boarding_point_id=points[0].pk, alighting_point_id=points[-1].pk)
    return SimpleNamespace(driver=users[0], passenger=users[1], other=users[2],
                           offer=offer, booking=booking, points=points, departure=departure)
