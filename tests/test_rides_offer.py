"""Feature 002 / T001–T002 locais / roadmap T013 — REQ-004, REQ-002, REQ-003."""

from datetime import timedelta
from decimal import Decimal
from importlib import import_module
from itertools import count

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import ProtectedError
from django.utils import timezone

pytestmark = pytest.mark.django_db


@pytest.fixture
def driver_factory():
    sequence = count(1)

    def create(email=None, role="MOTORISTA", status="ATIVA", enabled=True):
        user = get_user_model().objects.create_user(
            email=email or f"pessoa.sintetica{next(sequence)}@univille.br", full_name="Pessoa Sintética", role=role,
        )
        user.academic_status = status
        user.is_active = enabled
        user.save()
        return user
    return create


@pytest.fixture
def active_driver(driver_factory):
    return driver_factory()


@pytest.fixture
def pending_driver(driver_factory):
    return driver_factory(status="PENDENTE")


@pytest.fixture
def active_passenger(driver_factory):
    return driver_factory(role="PASSAGEIRO")


@pytest.fixture
def offer_factory(active_driver):
    def create(**overrides):
        point = apps.get_model("rides", "RoutePoint")
        values = dict(
            driver=active_driver, origin=point.objects.get(code="terminal-central"),
            destination=point.objects.get(code="campus-univille"),
            departure_at=timezone.now() + timedelta(days=1), seats=3,
            vehicle_model="  Veículo Demo  ", vehicle_color=" Azul ", vehicle_plate=" ficticio ",
        )
        values.update(overrides)
        return apps.get_model("rides", "RideOffer").objects.create(**values)
    return create


def test_app_configuration():
    assert apps.is_installed("rides")
    assert apps.get_app_config("rides").default_auto_field == "django.db.models.BigAutoField"
    assert connection.vendor == "postgresql"


def test_model_seed_catalog():
    point = apps.get_model("rides", "RoutePoint")
    assert dict(point.objects.values_list("code", "name")) == {
        "terminal-central": "Terminal Central", "bairro-america": "Bairro América",
        "campus-univille": "Campus Univille", "terminal-norte": "Terminal Norte",
    }
    assert point.objects.create(code="ponto-demo", name="  Ponto Sintético  ").name == "Ponto Sintético"


@pytest.mark.parametrize("code,name", [("", "Ponto"), ("invalido!", "Ponto"),
                                       ("a" * 81, "Ponto"), ("demo", "  "), ("demo", "a" * 101)])
def test_model_point_validation(code, name):
    with pytest.raises(ValidationError):
        apps.get_model("rides", "RoutePoint").objects.create(code=code, name=name)


def test_model_point_code_unique_sql():
    point = apps.get_model("rides", "RoutePoint")
    with pytest.raises(IntegrityError), transaction.atomic():
        point.objects.bulk_create([point(code="terminal-central", name="Duplicado Sintético")])


def test_model_offer_persistence_and_order(offer_factory):
    offer = offer_factory()
    assert offer.vehicle_model == "Veículo Demo"
    assert offer.vehicle_color == "Azul" and offer.vehicle_plate == "FICTICIO"
    assert offer.created_at and offer.seats == 3
    point = apps.get_model("rides", "RoutePoint")
    waypoint = apps.get_model("rides", "Waypoint")
    waypoint.objects.create(offer=offer, point=point.objects.get(code="terminal-norte"), position=2)
    waypoint.objects.create(offer=offer, point=point.objects.get(code="bairro-america"), position=1)
    assert list(offer.waypoints.values_list("point__code", flat=True)) == ["bairro-america", "terminal-norte"]
    assert list(offer.waypoints.values_list("position", flat=True)) == [1, 2]


def test_model_direct_offer_and_snapshot(offer_factory):
    first = offer_factory()
    assert not first.waypoints.exists()
    second = offer_factory(vehicle_model="Outro Demo", vehicle_plate="outra")
    first.refresh_from_db()
    assert first.vehicle_model == "Veículo Demo" and first.vehicle_plate == "FICTICIO"
    assert second.vehicle_plate == "OUTRA"


@pytest.mark.parametrize("fixture", ["pending_driver", "active_passenger"])
def test_model_driver_restriction(offer_factory, request, fixture):
    with pytest.raises(ValidationError) as error:
        offer_factory(driver=request.getfixturevalue(fixture))
    assert "driver" in error.value.message_dict


def test_model_disabled_or_stale_driver_rejected(offer_factory, active_driver):
    get_user_model().objects.filter(pk=active_driver.pk).update(is_active=False)
    with pytest.raises(ValidationError) as error:
        offer_factory(driver=active_driver)
    assert "driver" in error.value.message_dict


@pytest.mark.parametrize("seats", [0, -1, 1.5, Decimal("2.5"), "1.5", True, 9223372036854775808])
def test_model_seats_rejected(offer_factory, seats):
    with pytest.raises(ValidationError) as error:
        offer_factory(seats=seats)
    assert "seats" in error.value.message_dict


@pytest.mark.parametrize("seats", [1, 9223372036854775807])
def test_model_seats_boundaries(offer_factory, seats):
    assert offer_factory(seats=seats).seats == seats


@pytest.mark.parametrize("field,value", [("vehicle_model", "  "), ("vehicle_color", "  "),
                                        ("vehicle_plate", "  "), ("vehicle_model", "a" * 101),
                                        ("vehicle_color", "a" * 51), ("vehicle_plate", "a" * 21)])
def test_model_vehicle_fields(offer_factory, field, value):
    with pytest.raises(ValidationError) as error:
        offer_factory(**{field: value})
    assert field in error.value.message_dict


@pytest.mark.parametrize("offset", [-1, 0])
def test_model_future_departure(offer_factory, monkeypatch, offset):
    now = timezone.now()
    monkeypatch.setattr(timezone, "now", lambda: now)
    with pytest.raises(ValidationError) as error:
        offer_factory(departure_at=now + timedelta(seconds=offset))
    assert "departure_at" in error.value.message_dict


def test_model_naive_datetime_rejected(offer_factory):
    with pytest.raises(ValidationError) as error:
        offer_factory(departure_at=(timezone.now() + timedelta(days=1)).replace(tzinfo=None))
    assert "departure_at" in error.value.message_dict


def test_model_historical_offer_can_be_saved(offer_factory, monkeypatch):
    offer = offer_factory()
    monkeypatch.setattr(timezone, "now", lambda: offer.departure_at + timedelta(days=1))
    offer.save()
    offer.refresh_from_db()
    assert offer.seats == 3


def test_model_distinct_endpoints(offer_factory):
    point = apps.get_model("rides", "RoutePoint").objects.first()
    with pytest.raises(ValidationError):
        offer_factory(origin=point, destination=point)


@pytest.mark.parametrize("change", [{"seats": 0}, {"destination_id": "origin"}])
def test_model_offer_sql_checks(offer_factory, change):
    offer = offer_factory()
    values = {key: offer.origin_id if value == "origin" else value for key, value in change.items()}
    with pytest.raises(IntegrityError), transaction.atomic():
        type(offer).objects.filter(pk=offer.pk).update(**values)


@pytest.mark.parametrize("position", [0, -1, 1.5, 2147483648])
def test_model_waypoint_position(offer_factory, position):
    offer = offer_factory()
    point = apps.get_model("rides", "RoutePoint").objects.get(code="bairro-america")
    with pytest.raises(ValidationError):
        apps.get_model("rides", "Waypoint").objects.create(offer=offer, point=point, position=position)


@pytest.mark.parametrize("endpoint", ["origin", "destination"])
def test_model_waypoint_cannot_be_endpoint(offer_factory, endpoint):
    offer = offer_factory()
    with pytest.raises(ValidationError):
        apps.get_model("rides", "Waypoint").objects.create(offer=offer, point=getattr(offer, endpoint), position=1)


@pytest.mark.parametrize("case", ["position", "point", "zero"])
def test_model_waypoint_sql_constraints(offer_factory, case):
    offer = offer_factory()
    point = apps.get_model("rides", "RoutePoint")
    waypoint = apps.get_model("rides", "Waypoint")
    america = point.objects.get(code="bairro-america")
    north = point.objects.get(code="terminal-norte")
    waypoint.objects.create(offer=offer, point=america, position=1)
    duplicate = waypoint(offer=offer, point=north if case != "point" else america,
                         position=1 if case == "position" else (0 if case == "zero" else 2))
    with pytest.raises(IntegrityError), transaction.atomic():
        waypoint.objects.bulk_create([duplicate])


def test_model_delete_protection_and_cascade(offer_factory):
    offer = offer_factory()
    waypoint = apps.get_model("rides", "Waypoint")
    point = apps.get_model("rides", "RoutePoint").objects.get(code="bairro-america")
    waypoint.objects.create(offer=offer, point=point, position=1)
    for protected in (offer.driver, offer.origin, offer.destination, point):
        with pytest.raises(ProtectedError):
            protected.delete()
    offer.delete()
    assert not waypoint.objects.exists()
    assert type(point).objects.filter(pk=point.pk).exists()


def test_model_offer_default_order(offer_factory):
    now = timezone.now()
    later = offer_factory(departure_at=now + timedelta(days=2))
    earlier = offer_factory(departure_at=now + timedelta(days=1))
    tie = offer_factory(departure_at=earlier.departure_at)
    assert list(type(later).objects.values_list("pk", flat=True)) == [earlier.pk, tie.pk, later.pk]


def test_model_seed_migration_reversible():
    migration = import_module("rides.migrations.0002_seed_route_points")
    point = apps.get_model("rides", "RoutePoint")
    with connection.schema_editor() as editor:
        migration.remove_points(apps, editor)
        assert not point.objects.exists()
        migration.seed_points(apps, editor)
        migration.seed_points(apps, editor)
    assert point.objects.count() == 4


@pytest.mark.parametrize("field", ["driver", "origin", "destination", "departure_at", "seats"])
def test_model_required_offer_fields(offer_factory, field):
    with pytest.raises(ValidationError) as error:
        offer_factory(**{field: None})
    assert field in error.value.message_dict


def test_model_waypoint_foreign_key_sql(offer_factory):
    offer = offer_factory()
    waypoint = apps.get_model("rides", "Waypoint")
    with pytest.raises(IntegrityError), transaction.atomic():
        waypoint.objects.bulk_create([waypoint(offer=offer, point_id=999999, position=1)])
        connection.check_constraints()


def test_model_waypoint_required_fields():
    with pytest.raises(ValidationError):
        apps.get_model("rides", "Waypoint").objects.create(position=None)
