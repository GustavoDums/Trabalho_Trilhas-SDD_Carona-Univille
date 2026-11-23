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
from django.urls import reverse
from django.test import Client
from django.contrib.messages import get_messages

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


@pytest.fixture
def publication_data():
    points = apps.get_model("rides", "RoutePoint").objects
    return {
        "origin": points.get(code="terminal-central").pk,
        "destination": points.get(code="campus-univille").pk,
        "departure_at": timezone.localtime(timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
        "seats": "3", "vehicle_model": "Veículo Sintético", "vehicle_color": "Azul", "vehicle_plate": "FICTICIO",
        "waypoints-TOTAL_FORMS": "0", "waypoints-INITIAL_FORMS": "0",
    }


def test_publish_get(client, active_driver):
    client.force_login(active_driver)
    response = client.get(reverse("rides:offer-create"))
    assert response.status_code == 200
    html = response.content.decode()
    assert 'name="csrfmiddlewaretoken"' in html
    assert 'name="waypoints-TOTAL_FORMS"' in html
    assert "America/Sao_Paulo" in html
    assert 'type="datetime-local"' in html
    assert 'name="driver"' not in html
    assert "Adicionar parada" in html


@pytest.mark.parametrize("with_stops", [False, True])
def test_publish_valid_atomic_offer(client, active_driver, driver_factory, publication_data, with_stops):
    client.force_login(active_driver)
    other = driver_factory()
    data = dict(publication_data, driver=other.pk, user_id=other.pk)
    if with_stops:
        points = apps.get_model("rides", "RoutePoint").objects
        data.update({"waypoints-TOTAL_FORMS": "2",
                     "waypoints-0-point": points.get(code="terminal-norte").pk,
                     "waypoints-1-point": points.get(code="bairro-america").pk,
                     "waypoints-0-position": "99"})
    response = client.post(reverse("rides:offer-create"), data)
    assert response.status_code == 302 and response.url == "/caronas/minhas-ofertas/"
    offer = apps.get_model("rides", "RideOffer").objects.get()
    assert offer.driver == active_driver and offer.seats == 3
    assert offer.vehicle_plate == "FICTICIO"
    assert timezone.is_aware(offer.departure_at)
    expected = ["terminal-norte", "bairro-america"] if with_stops else []
    assert list(offer.waypoints.values_list("point__code", flat=True)) == expected
    assert list(offer.waypoints.values_list("position", flat=True)) == ([1, 2] if with_stops else [])
    assert [str(m) for m in get_messages(response.wsgi_request)] == ["Oferta de carona publicada com sucesso."]


@pytest.mark.parametrize("identity,status,url", [("anonymous", 302, "/accounts/login/"),
                                                ("pending_driver", 302, "/accounts/activation/"),
                                                ("active_passenger", 403, "")])
@pytest.mark.parametrize("method", ["get", "post"])
def test_publish_permissions(client, request, publication_data, identity, status, url, method):
    if identity != "anonymous":
        client.force_login(request.getfixturevalue(identity))
    response = getattr(client, method)(reverse("rides:offer-create"), publication_data if method == "post" else {})
    assert response.status_code == status
    if url:
        assert response.url.startswith(url)
    assert not apps.get_model("rides", "RideOffer").objects.exists()


@pytest.mark.parametrize("field,value", [("seats", "1.5"), ("vehicle_plate", ""),
                                        ("departure_at", "2000-01-01T12:00")])
def test_publish_invalid_fields(client, active_driver, publication_data, field, value):
    client.force_login(active_driver)
    response = client.post(reverse("rides:offer-create"), dict(publication_data, **{field: value}))
    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert not apps.get_model("rides", "RideOffer").objects.exists()


def test_publish_repeated_route_rejected(client, active_driver, publication_data):
    client.force_login(active_driver)
    data = dict(publication_data)
    data.update({"waypoints-TOTAL_FORMS": "1", "waypoints-0-point": data["origin"]})
    response = client.post(reverse("rides:offer-create"), data)
    assert response.status_code == 200
    assert not apps.get_model("rides", "RideOffer").objects.exists()
    assert not apps.get_model("rides", "Waypoint").objects.exists()


def test_publish_csrf(client, active_driver, publication_data):
    client = Client(enforce_csrf_checks=True)
    client.force_login(active_driver)
    url = reverse("rides:offer-create")
    assert client.post(url, publication_data).status_code == 403
    assert client.get(url).status_code == 200
    publication_data["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
    assert client.post(url, publication_data).status_code == 302


def test_publish_service_rolls_back_second_stop(active_driver, monkeypatch):
    from rides.services import publish_offer
    point = apps.get_model("rides", "RoutePoint").objects
    waypoint = apps.get_model("rides", "Waypoint")
    original = waypoint.save

    def failing_save(instance, *args, **kwargs):
        if instance.position == 2:
            raise RuntimeError("Falha sintética na segunda parada")
        return original(instance, *args, **kwargs)

    monkeypatch.setattr(waypoint, "save", failing_save)
    data = dict(origin=point.get(code="terminal-central"), destination=point.get(code="campus-univille"),
                departure_at=timezone.now() + timedelta(days=1), seats=2,
                vehicle_model="Demo", vehicle_color="Azul", vehicle_plate="FICTICIO")
    with pytest.raises(RuntimeError):
        publish_offer(driver=active_driver, data=data,
                      points=[point.get(code="bairro-america"), point.get(code="terminal-norte")])
    assert not apps.get_model("rides", "RideOffer").objects.exists()
    assert not waypoint.objects.exists()


def test_publish_service_rechecks_driver(active_driver):
    from django.core.exceptions import PermissionDenied
    from rides.services import publish_offer
    get_user_model().objects.filter(pk=active_driver.pk).update(academic_status="PENDENTE")
    with pytest.raises(PermissionDenied):
        publish_offer(driver=active_driver, data={}, points=[])
    assert not apps.get_model("rides", "RideOffer").objects.exists()


def test_vehicle_prefill_only_latest_own_offer(client, active_driver, driver_factory, offer_factory):
    offer_factory(vehicle_model="Antigo Demo")
    latest = offer_factory(vehicle_model="Último Demo", vehicle_color="Verde", vehicle_plate="ultima")
    offer_factory(driver=driver_factory(), vehicle_model="Alheio Demo", vehicle_plate="ALHEIA")
    client.force_login(active_driver)
    response = client.get(reverse("rides:offer-create"), {"driver": "999999"})
    initial = response.context["form"].initial
    assert initial == {"vehicle_model": latest.vehicle_model, "vehicle_color": "Verde", "vehicle_plate": "ULTIMA"}
    assert "ALHEIA" not in response.content.decode()


def test_vehicle_first_offer_does_not_prefill_other_author(client, active_driver, driver_factory, offer_factory):
    offer_factory(driver=driver_factory(), vehicle_plate="SEGREDOALHEIO")
    client.force_login(active_driver)
    response = client.get(reverse("rides:offer-create"))
    assert not response.context["form"].initial
    assert "SEGREDOALHEIO" not in response.content.decode()


def test_vehicle_reuse_submission_preserves_previous_snapshot(client, active_driver, offer_factory, publication_data):
    first = offer_factory(vehicle_model="Primeiro Demo", vehicle_color="Azul", vehicle_plate="PRIMEIRA")
    before = type(first).objects.values().get(pk=first.pk)
    client.force_login(active_driver)
    data = dict(publication_data, vehicle_model="Novo Demo", vehicle_color="Verde", vehicle_plate=" nova ")
    assert client.post(reverse("rides:offer-create"), data).status_code == 302
    assert type(first).objects.values().get(pk=first.pk) == before
    assert type(first).objects.exclude(pk=first.pk).get().vehicle_plate == "NOVA"


@pytest.mark.parametrize("field,value", [
    ("vehicle_model", ""), ("vehicle_model", "  "), ("vehicle_color", ""),
    ("vehicle_color", "  "), ("vehicle_plate", "  "), ("seats", "0"),
    ("seats", "-1"), ("seats", "1.5"), ("origin", "999999"),
    ("destination", ""), ("departure_at", "2000-01-01T12:00"),
])
def test_invalid_offer_preserves_fields_and_clears_plate(client, active_driver, publication_data, field, value):
    client.force_login(active_driver)
    data = dict(publication_data, **{field: value})
    response = client.post(reverse("rides:offer-create"), data)
    assert response.status_code == 200
    form = response.context["form"]
    assert field in form.errors
    assert form["vehicle_plate"].value() == ""
    assert form["vehicle_color"].value() == data["vehicle_color"]
    assert "Informe novamente a placa" in response.content.decode()
    assert not apps.get_model("rides", "RideOffer").objects.exists()
    assert not apps.get_model("rides", "Waypoint").objects.exists()


@pytest.mark.parametrize("management", ["missing", "negative", "invalid", "initial"])
def test_invalid_management_form(client, active_driver, publication_data, management):
    client.force_login(active_driver)
    data = dict(publication_data)
    if management == "missing":
        del data["waypoints-TOTAL_FORMS"]
    elif management == "negative":
        data["waypoints-TOTAL_FORMS"] = "-1"
    elif management == "initial":
        data["waypoints-INITIAL_FORMS"] = "1"
    else:
        data["waypoints-TOTAL_FORMS"] = "invalido"
    response = client.post(reverse("rides:offer-create"), data)
    assert response.status_code == 200
    assert response.context["waypoint_formset"].non_form_errors()
    assert response.context["form"]["vehicle_plate"].value() == ""
    assert not apps.get_model("rides", "RideOffer").objects.exists()


@pytest.mark.parametrize("kind", ["empty", "unknown", "repeated", "endpoint"])
def test_invalid_stop_rejects_complete_publication(client, active_driver, publication_data, kind):
    client.force_login(active_driver)
    data = dict(publication_data)
    america = apps.get_model("rides", "RoutePoint").objects.get(code="bairro-america").pk
    second = {"empty": "", "unknown": "999999", "repeated": america, "endpoint": data["origin"]}[kind]
    data.update({"waypoints-TOTAL_FORMS": "2", "waypoints-0-point": america, "waypoints-1-point": second})
    response = client.post(reverse("rides:offer-create"), data)
    assert response.status_code == 200
    assert response.context["waypoint_formset"][0]["point"].value() == str(america)
    assert response.context["form"]["vehicle_plate"].value() == ""
    assert not apps.get_model("rides", "RideOffer").objects.exists()
    assert not apps.get_model("rides", "Waypoint").objects.exists()


def test_invalid_departure_exactly_now(client, active_driver, publication_data, monkeypatch):
    now = timezone.now().replace(second=0, microsecond=0)
    monkeypatch.setattr(timezone, "now", lambda: now)
    client.force_login(active_driver)
    data = dict(publication_data, departure_at=timezone.localtime(now).strftime("%Y-%m-%dT%H:%M"))
    response = client.post(reverse("rides:offer-create"), data)
    assert response.status_code == 200
    assert "departure_at" in response.context["form"].errors
    assert not apps.get_model("rides", "RideOffer").objects.exists()


def test_invalid_correction_then_resubmit(client, active_driver, publication_data):
    client.force_login(active_driver)
    url = reverse("rides:offer-create")
    assert client.post(url, dict(publication_data, seats="0")).status_code == 200
    assert client.post(url, publication_data).status_code == 302
    assert apps.get_model("rides", "RideOffer").objects.count() == 1


def test_invalid_same_endpoints(client, active_driver, publication_data):
    client.force_login(active_driver)
    response = client.post(reverse("rides:offer-create"), dict(publication_data, destination=publication_data["origin"]))
    assert response.status_code == 200
    assert "destination" in response.context["form"].errors
    assert response.context["form"]["vehicle_plate"].value() == ""
    assert not apps.get_model("rides", "RideOffer").objects.exists()


def test_invalid_service_error_returns_field_feedback(client, active_driver, publication_data, monkeypatch):
    def fail_publication(**kwargs):
        raise ValidationError({"departure_at": "A saída deve ser estritamente futura."})

    monkeypatch.setattr("rides.views.publish_offer", fail_publication)
    client.force_login(active_driver)
    response = client.post(reverse("rides:offer-create"), publication_data)
    assert response.status_code == 200
    assert "departure_at" in response.context["form"].errors
    assert response.context["form"]["vehicle_plate"].value() == ""
    assert not apps.get_model("rides", "RideOffer").objects.exists()


def test_invalid_service_unknown_catalog_point(offer_factory, active_driver):
    from rides.services import publish_offer
    source = offer_factory()
    data = {field: getattr(source, field) for field in (
        "origin", "destination", "departure_at", "seats", "vehicle_model", "vehicle_color", "vehicle_plate",
    )}
    phantom = apps.get_model("rides", "RoutePoint")(pk=999999, code="sintetico-ausente", name="Ponto Sintético")
    with pytest.raises(ValidationError, match="catálogo"):
        publish_offer(driver=active_driver, data=data, points=[phantom])
    assert type(source).objects.count() == 1
    assert not apps.get_model("rides", "Waypoint").objects.exists()


def test_my_offers_empty(client, active_driver):
    client.force_login(active_driver)
    response = client.get(reverse("rides:my-offers"))
    assert response.status_code == 200
    html = response.content.decode()
    assert "Você ainda não publicou ofertas de carona." in html
    assert reverse("rides:offer-create") in html


def test_my_offers_order_itinerary_and_privacy(client, active_driver, driver_factory, offer_factory):
    now = timezone.now()
    later = offer_factory(departure_at=now + timedelta(days=2), vehicle_model="Demo Posterior")
    earlier = offer_factory(departure_at=now + timedelta(days=1), vehicle_model="Demo Primeiro")
    tied = offer_factory(departure_at=earlier.departure_at, vehicle_model="Demo Empatado")
    other = driver_factory()
    offer_factory(driver=other, vehicle_model="Veículo Alheio", vehicle_plate="PLACAALHEIA")
    point = apps.get_model("rides", "RoutePoint").objects
    waypoint = apps.get_model("rides", "Waypoint")
    waypoint.objects.create(offer=earlier, point=point.get(code="terminal-norte"), position=1)
    waypoint.objects.create(offer=earlier, point=point.get(code="bairro-america"), position=2)
    client.force_login(active_driver)
    response = client.get(reverse("rides:my-offers"), {"driver": other.pk, "user_id": other.pk})
    assert response.status_code == 200
    assert [offer.pk for offer in response.context["offers"]] == [earlier.pk, tied.pk, later.pk]
    html = response.content.decode()
    assert "Veículo Alheio" not in html
    for secret in (other.email, active_driver.email, "PLACAALHEIA", "FICTICIO"):
        assert secret not in html
    assert html.index("Demo Primeiro") < html.index("Demo Empatado") < html.index("Demo Posterior")
    itinerary = html.split('data-offer-id="' + str(earlier.pk) + '"', 1)[1].split("</article>", 1)[0]
    assert itinerary.index("Terminal Central") < itinerary.index("Terminal Norte") < itinerary.index("Bairro América") < itinerary.index("Campus Univille")
    assert "3 vagas" in itinerary and "Azul" in itinerary and "America/Sao_Paulo" in html


@pytest.mark.parametrize("identity,status,prefix", [("anonymous", 302, "/accounts/login/"),
                                                  ("pending_driver", 302, "/accounts/activation/"),
                                                  ("active_passenger", 403, "")])
def test_my_offers_permissions(client, request, identity, status, prefix):
    if identity != "anonymous":
        client.force_login(request.getfixturevalue(identity))
    response = client.get(reverse("rides:my-offers"))
    assert response.status_code == status
    if prefix:
        assert response.url.startswith(prefix)


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_my_offers_rejects_writes(client, active_driver, offer_factory, method):
    offer = offer_factory()
    before = type(offer).objects.values().get(pk=offer.pk)
    client.force_login(active_driver)
    assert getattr(client, method)(reverse("rides:my-offers")).status_code == 405
    assert type(offer).objects.values().get(pk=offer.pk) == before


def test_my_offers_publication_redirect_reaches_list(client, active_driver, publication_data):
    client.force_login(active_driver)
    response = client.post(reverse("rides:offer-create"), publication_data, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [("/caronas/minhas-ofertas/", 302)]
    assert len(response.context["offers"]) == 1
    assert "Oferta de carona publicada com sucesso." in response.content.decode()


def test_my_offers_prefetch_avoids_per_stop_queries(client, active_driver, offer_factory, django_assert_num_queries):
    from rides.views import MyOffersView
    offer = offer_factory()
    point = apps.get_model("rides", "RoutePoint").objects.get(code="bairro-america")
    apps.get_model("rides", "Waypoint").objects.create(offer=offer, point=point, position=1)
    from django.test import RequestFactory
    request = RequestFactory().get("/caronas/minhas-ofertas/")
    request.user = active_driver
    view = MyOffersView()
    view.setup(request)
    with django_assert_num_queries(2):
        offers = list(view.get_queryset())
        for item in offers:
            assert item.origin.name and item.destination.name
            assert [stop.point.name for stop in item.waypoints.all()]
