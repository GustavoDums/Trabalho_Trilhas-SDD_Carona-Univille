"""Feature 004/T002 local — roadmap T020; REQ-006, REQ-002, REQ-017."""
from datetime import timedelta
from itertools import product
from types import SimpleNamespace

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from rides.models import RideOffer, RoutePoint, Waypoint

pytestmark = pytest.mark.django_db


def booking_model():
    return apps.get_model("rides", "RideBooking")


@pytest.fixture
def booking_scene(academic_user_factory):
    driver = academic_user_factory(role="MOTORISTA", password=None)
    passenger = academic_user_factory(password=None)
    for user in (driver, passenger):
        user.academic_status = "ATIVA"
        user.save(update_fields=["academic_status", "updated_at"])
    catalog = {point.code: point for point in RoutePoint.objects.all()}
    points = [catalog[code] for code in
              ("terminal-norte", "campus-univille", "bairro-america", "terminal-central")]
    offer = RideOffer.objects.create(
        driver=driver, origin=points[0], destination=points[3],
        departure_at=timezone.now()+timedelta(days=1), seats=3,
        vehicle_model="Veículo Sintético", vehicle_color="Azul", vehicle_plate="FICTICIO")
    Waypoint.objects.create(offer=offer, point=points[2], position=2)
    Waypoint.objects.create(offer=offer, point=points[1], position=1)
    return SimpleNamespace(driver=driver, passenger=passenger, offer=offer, points=points)


def new_booking(scene, **overrides):
    values = dict(offer=scene.offer, passenger=scene.passenger,
                  boarding_point=scene.points[0], alighting_point=scene.points[3])
    values.update(overrides)
    return booking_model()(**values)


def test_booking_fields_and_protection():
    model = booking_model()
    assert connection.vendor == "postgresql"
    assert model.Status.CONFIRMADA == "CONFIRMADA"
    assert model.Status.CANCELADA == "CANCELADA"
    assert set(model.Status.values) == {"CONFIRMADA", "CANCELADA"}
    assert model._meta.get_field("status").max_length == 10
    assert model._meta.get_field("status").default == "CONFIRMADA"
    for name in ("offer", "passenger", "boarding_point", "alighting_point"):
        field = model._meta.get_field(name)
        assert not field.null and field.remote_field.on_delete.__name__ == "PROTECT"
    assert set(field.name for field in model._meta.fields) == {
        "id", "offer", "passenger", "boarding_point", "alighting_point", "status",
        "created_at", "updated_at", "cancelled_at"}


def test_booking_default_and_no_side_effect_on_capacity(booking_scene):
    before = (list(RideOffer.objects.values()), list(RoutePoint.objects.values()),
              list(Waypoint.objects.values()), list(get_user_model().objects.values()))
    booking = new_booking(booking_scene)
    booking.save()
    booking.refresh_from_db()
    assert booking.status == "CONFIRMADA"
    assert booking.offer == booking_scene.offer and booking.passenger == booking_scene.passenger
    assert timezone.is_aware(booking.created_at) and timezone.is_aware(booking.updated_at)
    assert booking_scene.offer.bookings.get() == booking
    assert booking_scene.passenger.ride_bookings.get() == booking
    assert (list(RideOffer.objects.values()), list(RoutePoint.objects.values()),
            list(Waypoint.objects.values()), list(get_user_model().objects.values())) == before


def test_booking_update_timestamp_and_cancelled_history(booking_scene, monkeypatch):
    booking = new_booking(booking_scene)
    booking.save()
    created = booking.created_at
    later = booking.updated_at + timedelta(seconds=1)
    monkeypatch.setattr(timezone, "now", lambda: later)
    get_user_model().objects.filter(pk=booking_scene.passenger.pk).update(academic_status="PENDENTE")
    booking.status = "CANCELADA"
    booking.save()
    booking.refresh_from_db()
    assert booking.created_at == created and booking.updated_at == later
    assert booking.status == "CANCELADA"


def test_booking_rejects_self_even_if_driver_role_was_changed(booking_scene):
    # Cross-table author check must remain independent of the account role check.
    get_user_model().objects.filter(pk=booking_scene.driver.pk).update(role="PASSAGEIRO")
    booking = new_booking(booking_scene, passenger=booking_scene.driver)
    with pytest.raises(ValidationError) as error:
        booking.save()
    assert "passenger" in error.value.message_dict
    assert any("própria" in message for message in error.value.message_dict["passenger"])
    assert not booking_model().objects.exists()


@pytest.mark.parametrize("changes", [
    {"academic_status": "PENDENTE"}, {"is_active": False}, {"role": "MOTORISTA"},
])
def test_booking_new_passenger_must_be_eligible(booking_scene, changes):
    get_user_model().objects.filter(pk=booking_scene.passenger.pk).update(**changes)
    with pytest.raises(ValidationError) as error:
        new_booking(booking_scene).save()
    assert "passenger" in error.value.message_dict
    assert not booking_model().objects.exists()


@pytest.mark.parametrize("boarding,alighting", list(product(range(4), repeat=2)))
def test_booking_all_itinerary_pairs(booking_scene, boarding, alighting):
    booking = new_booking(
        booking_scene, boarding_point=booking_scene.points[boarding],
        alighting_point=booking_scene.points[alighting])
    if boarding < alighting:
        booking.save()
        assert booking.pk
    else:
        with pytest.raises(ValidationError) as error:
            booking.save()
        assert "alighting_point" in error.value.message_dict
        assert not booking_model().objects.exists()


@pytest.mark.parametrize("field", ["boarding_point", "alighting_point"])
def test_booking_point_outside_offer(booking_scene, field):
    outsider = RoutePoint.objects.create(code="ponto-fora", name="Ponto Sintético Externo")
    with pytest.raises(ValidationError) as error:
        new_booking(booking_scene, **{field: outsider}).save()
    assert field in error.value.message_dict


def test_booking_direct_route_and_ambiguous_legacy_data(booking_scene):
    booking_scene.offer.waypoints.all().delete()
    booking = new_booking(booking_scene)
    booking.save()
    # Historical malformed itinerary, bypassing Python clean but not SQL constraints.
    Waypoint.objects.bulk_create([
        Waypoint(offer=booking_scene.offer, point=booking_scene.points[0], position=1)])
    with pytest.raises(ValidationError):
        booking.full_clean()


@pytest.mark.parametrize("field", ["offer", "passenger", "boarding_point", "alighting_point"])
def test_booking_required_relations(booking_scene, field):
    with pytest.raises(ValidationError) as error:
        new_booking(booking_scene, **{field: None}).save()
    assert field in error.value.message_dict


@pytest.mark.parametrize("field", ["offer_id", "passenger_id", "boarding_point_id", "alighting_point_id"])
def test_booking_invalid_foreign_keys_are_validation_errors(booking_scene, field):
    booking = new_booking(booking_scene)
    setattr(booking, field, 999999999)
    with pytest.raises(ValidationError):
        booking.save()


@pytest.mark.parametrize("status", ["", "PENDENTE", "confirmada", "X" * 11])
def test_booking_invalid_status_in_model(booking_scene, status):
    with pytest.raises(ValidationError) as error:
        new_booking(booking_scene, status=status).save()
    assert "status" in error.value.message_dict


def test_booking_active_uniqueness_in_model(booking_scene):
    new_booking(booking_scene).save()
    with pytest.raises(ValidationError):
        new_booking(booking_scene, boarding_point=booking_scene.points[1]).save()
    assert booking_model().objects.count() == 1


def test_booking_active_uniqueness_in_postgresql(booking_scene):
    new_booking(booking_scene).save()
    with pytest.raises(IntegrityError), transaction.atomic():
        booking_model().objects.bulk_create([new_booking(booking_scene)])
    assert booking_model().objects.count() == 1


@pytest.mark.parametrize("bad", ["status", "points"])
def test_booking_sql_checks_cannot_be_bypassed(booking_scene, bad):
    booking = new_booking(booking_scene)
    booking.save()
    values = {"status": "PENDENTE"} if bad == "status" else {
        "alighting_point_id": booking.boarding_point_id}
    with pytest.raises(IntegrityError), transaction.atomic():
        booking_model().objects.filter(pk=booking.pk).update(**values)
    booking.refresh_from_db()
    assert booking.status == "CONFIRMADA"
    assert booking.boarding_point_id != booking.alighting_point_id


def test_booking_cancelled_records_allow_new_active_without_erasing_history(booking_scene):
    for _ in range(2):
        new_booking(booking_scene, status="CANCELADA").save()
    active = new_booking(booking_scene)
    active.save()
    assert booking_model().objects.count() == 3
    assert booking_model().objects.filter(status="CONFIRMADA").count() == 1
    booking_scene.offer.refresh_from_db()
    assert booking_scene.offer.seats == 3


def test_booking_other_passenger_or_offer_is_not_a_duplicate(booking_scene, academic_user_factory):
    new_booking(booking_scene).save()
    passenger = academic_user_factory(password=None)
    passenger.academic_status = "ATIVA"
    passenger.save(update_fields=["academic_status", "updated_at"])
    new_booking(booking_scene, passenger=passenger).save()
    other = RideOffer.objects.create(
        driver=booking_scene.driver, origin=booking_scene.points[0], destination=booking_scene.points[3],
        departure_at=timezone.now()+timedelta(days=2), seats=3,
        vehicle_model="Outro Sintético", vehicle_color="Verde", vehicle_plate="FICTICIO")
    new_booking(booking_scene, offer=other).save()
    assert booking_model().objects.count() == 3


@pytest.mark.parametrize("target", ["offer", "passenger", "boarding_point", "alighting_point"])
def test_booking_historical_relations_are_protected(booking_scene, target):
    booking = new_booking(booking_scene, status="CANCELADA")
    booking.save()
    with pytest.raises(ProtectedError):
        getattr(booking, target).delete()
    assert booking_model().objects.filter(pk=booking.pk).exists()


def test_booking_migration_schema_on_postgresql():
    model = booking_model()
    from django.db.migrations.recorder import MigrationRecorder
    assert MigrationRecorder(connection).migration_qs.filter(
        app="rides", name="0003_ridebooking").exists()
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, model._meta.db_table)
    assert constraints["booking_active_passenger_unique"]["unique"]
    assert constraints["booking_status_valid"]["check"]
    assert constraints["booking_points_distinct"]["check"]
    assert all(any(info.get("foreign_key") for info in constraints.values()
                   if name in info["columns"])
               for name in ("offer_id", "passenger_id", "boarding_point_id", "alighting_point_id"))


# Feature 004/T004 local — roadmap T022; views/projeção isoladas, sem rotas.
@pytest.fixture
def presentation_scene(booking_scene, academic_user_factory):
    from rides.services.booking_service import BookingService
    scene = booking_scene
    scene.driver.full_name = "Motorista Exemplo"
    scene.driver.save()
    scene.passenger.full_name = "Passageiro Primeiro"
    scene.passenger.save()

    def active(role, name):
        user = academic_user_factory(role=role, full_name=name, password=None)
        user.academic_status = "ATIVA"
        user.save(update_fields=["academic_status", "updated_at"])
        return user

    scene.second = active("PASSAGEIRO", "Passageiro Segundo")
    scene.outsider = active("PASSAGEIRO", "Pessoa Externa")
    scene.other_driver = active("MOTORISTA", "Condutor Externo")
    scene.other_offer = RideOffer.objects.create(
        driver=scene.other_driver, origin=scene.points[0], destination=scene.points[-1],
        departure_at=timezone.now()+timedelta(days=2), seats=2,
        vehicle_model="Outro Sintético", vehicle_color="Verde", vehicle_plate="PLACA-EXTERNA")
    def book(passenger, offer):
        return BookingService.create_booking(
            passenger=passenger, offer_id=offer.pk,
            boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk)
    scene.first_booking = book(scene.passenger, scene.offer)
    scene.second_booking = book(scene.second, scene.offer)
    scene.external_booking = book(scene.outsider, scene.other_offer)
    return scene


def private_api():
    from importlib import import_module
    return import_module("rides.services.booking_queries")


def prepared_request(method, user, data=None, path="/caronas/minhas-reservas/"):
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.messages.middleware import MessageMiddleware
    from django.test import RequestFactory
    request = getattr(RequestFactory(), method)(path, data=data or {})
    SessionMiddleware(lambda request: None).process_request(request)
    MessageMiddleware(lambda request: None).process_request(request)
    request.user = user
    return request


def private_view(scene, *, user=None, data=None):
    from rides import views
    request = prepared_request("get", user or scene.passenger, data)
    response = views.MyBookingsView.as_view()(request)
    response.render()
    return response


def reserve_view(scene, *, user=None, data=None, method="post", offer_id=None):
    from rides import views
    request = prepared_request(method, user or scene.outsider, data,
                               path=f"/caronas/{scene.offer.pk}/reservar/")
    response = views.BookRideView.as_view()(request, offer_id=offer_id or scene.offer.pk)
    if hasattr(response, "render"):
        response.render()
    return response


def valid_booking_post(scene):
    return {"boarding_point_id": str(scene.points[0].pk),
            "alighting_point_id": str(scene.points[-1].pk)}


@pytest.mark.parametrize("who,expected_ids", [
    ("passenger", ["first_booking"]), ("second", ["second_booking"]),
    ("driver", ["first_booking", "second_booking"]), ("outsider", ["external_booking"]),
    ("other_driver", ["external_booking"]),
])
def test_private_projection_only_current_participants(presentation_scene, who, expected_ids):
    scene = presentation_scene
    result = private_api().BookingQueryService.list_for(user=getattr(scene, who))
    assert isinstance(result, tuple)
    assert [entry.booking_id for entry in result] == [getattr(scene, name).pk for name in expected_ids]
    assert all(isinstance(entry, private_api().BookingSummary) for entry in result)


@pytest.mark.parametrize("who", ["passenger", "driver"])
def test_private_confirmed_counterpart_full_name_plate_but_no_email(presentation_scene, who):
    from dataclasses import fields, FrozenInstanceError
    scene = presentation_scene
    dto = private_api().BookingQueryService.list_for(user=getattr(scene, who))[0]
    counterpart = scene.driver if who == "passenger" else scene.passenger
    assert dto.counterpart_name == counterpart.full_name
    assert dto.vehicle_plate == scene.offer.vehicle_plate
    assert dto.boarding_name == scene.points[0].name
    assert dto.alighting_name == scene.points[-1].name
    assert {field.name for field in fields(dto)} == {
        "booking_id", "offer_id", "status", "departure_at", "boarding_name",
        "alighting_name", "counterpart_role", "counterpart_name", "vehicle_model",
        "vehicle_color", "vehicle_plate"}
    assert "@" not in repr(dto)
    with pytest.raises(FrozenInstanceError):
        dto.counterpart_name = "Outra Pessoa"


@pytest.mark.parametrize("who", ["passenger", "driver"])
def test_private_cancelled_projection_and_html_revoke_private_fields(presentation_scene, who):
    scene = presentation_scene
    booking_model().objects.filter(offer=scene.offer).update(status="CANCELADA")
    result = private_api().BookingQueryService.list_for(user=getattr(scene, who))
    counterpart = scene.driver if who == "passenger" else scene.passenger
    assert result[0].counterpart_name == counterpart.display_name
    assert all(entry.vehicle_plate is None for entry in result)
    html = private_view(scene, user=getattr(scene, who)).content.decode()
    assert scene.driver.full_name not in html and scene.passenger.full_name not in html
    assert scene.second.full_name not in html and scene.offer.vehicle_plate not in html
    assert "CANCELADA" in html
    assert "Dados privados indisponíveis" in html


def test_private_html_ignores_ids_of_third_parties_and_exposes_only_dtos(presentation_scene):
    scene = presentation_scene
    response = private_view(scene, data={
        "user_id": scene.driver.pk, "booking_id": scene.external_booking.pk,
        "passenger_id": scene.second.pk, "offer_id": scene.other_offer.pk})
    assert response.status_code == 200
    assert [dto.booking_id for dto in response.context_data["bookings"]] == [scene.first_booking.pk]
    html = response.content.decode()
    assert scene.driver.full_name in html and scene.offer.vehicle_plate in html
    for secret in (scene.second.full_name, scene.outsider.full_name, scene.other_driver.full_name,
                   "PLACA-EXTERNA", scene.driver.email, scene.passenger.email, scene.second.email,
                   "application/json", "whatsapp"):
        assert secret not in html.lower() if secret == "whatsapp" else secret not in html


def test_private_html_escapes_counterpart_and_catalog_labels(presentation_scene):
    scene = presentation_scene
    get_user_model().objects.filter(pk=scene.driver.pk).update(full_name="<b>Nome Sintético</b>")
    RoutePoint.objects.filter(pk=scene.points[0].pk).update(name="<script>Ponto</script>")
    RideOffer.objects.filter(pk=scene.offer.pk).update(vehicle_plate="<img src=x>")
    html = private_view(scene).content.decode()
    assert "&lt;b&gt;Nome Sintético&lt;/b&gt;" in html
    assert "&lt;script&gt;Ponto&lt;/script&gt;" in html
    assert "&lt;img src=x&gt;" in html
    assert "<script>" not in html and "<img src=x>" not in html


@pytest.mark.parametrize("changes", [
    {"academic_status": "PENDENTE"}, {"is_active": False}, {"role": "OUTRO"},
])
def test_private_service_rechecks_stale_viewer(presentation_scene, changes):
    from django.core.exceptions import PermissionDenied
    user = presentation_scene.passenger
    get_user_model().objects.filter(pk=user.pk).update(**changes)
    with pytest.raises(PermissionDenied):
        private_api().BookingQueryService.list_for(user=user)


def test_private_service_rejects_anonymous_and_missing_user(presentation_scene):
    from django.contrib.auth.models import AnonymousUser
    from django.core.exceptions import PermissionDenied
    with pytest.raises(PermissionDenied):
        private_api().BookingQueryService.list_for(user=AnonymousUser())
    user = presentation_scene.passenger
    user.pk = 999999999
    with pytest.raises(PermissionDenied):
        private_api().BookingQueryService.list_for(user=user)


def test_private_list_empty_and_get_does_not_write_domain(booking_scene):
    scene = booking_scene
    models = (RideOffer, RoutePoint, Waypoint, get_user_model(), booking_model())
    before = tuple(list(model.objects.order_by("pk").values()) for model in models)
    response = private_view(scene)
    assert response.status_code == 200 and response.context_data["bookings"] == ()
    assert "Você ainda não tem reservas para consultar." in response.content.decode()
    assert tuple(list(model.objects.order_by("pk").values()) for model in models) == before


def test_private_queries_are_ordered_and_constant_as_list_grows(presentation_scene):
    from django.test.utils import CaptureQueriesContext
    from rides.services.booking_service import BookingService
    scene = presentation_scene
    with CaptureQueriesContext(connection) as first_queries:
        private_api().BookingQueryService.list_for(user=scene.driver)
    added = RideOffer.objects.create(
        driver=scene.driver, origin=scene.points[0], destination=scene.points[-1],
        departure_at=scene.offer.departure_at-timedelta(hours=1), seats=3,
        vehicle_model="Antecipado Sintético", vehicle_color="Azul", vehicle_plate="OUTRA")
    booking = BookingService.create_booking(
        passenger=scene.passenger, offer_id=added.pk,
        boarding_point_id=scene.points[0].pk, alighting_point_id=scene.points[-1].pk)
    with CaptureQueriesContext(connection) as last_queries:
        results = private_api().BookingQueryService.list_for(user=scene.driver)
    assert len(last_queries) == len(first_queries)
    assert [dto.booking_id for dto in results] == [
        booking.pk, scene.first_booking.pk, scene.second_booking.pk]


def test_book_view_uses_session_actor_and_fixed_redirect_ignoring_forged_fields(presentation_scene):
    from django.contrib.messages import get_messages
    from rides import views
    scene = presentation_scene
    request = prepared_request("post", scene.outsider, dict(
        valid_booking_post(scene), passenger_id=str(scene.second.pk), status="CANCELADA",
        offer_id=str(scene.other_offer.pk), next="https://example.invalid/"),
        path=f"/caronas/{scene.offer.pk}/reservar/")
    response = views.BookRideView.as_view()(request, offer_id=scene.offer.pk)
    assert response.status_code == 302 and response.url == "/caronas/minhas-reservas/"
    added = booking_model().objects.get(offer=scene.offer, passenger=scene.outsider)
    assert added.status == "CONFIRMADA"
    assert len(list(get_messages(request))) == 1
    assert scene.driver.email not in str(response.headers)


@pytest.mark.parametrize("field", ["boarding_point_id", "alighting_point_id"])
def test_book_view_invalid_form_does_not_call_service(presentation_scene, monkeypatch, field):
    from unittest.mock import Mock
    from rides.services.booking_service import BookingService
    scene = presentation_scene
    spy = Mock()
    monkeypatch.setattr(BookingService, "create_booking", spy)
    response = reserve_view(scene, data={**valid_booking_post(scene), field: "inválido"})
    assert response.status_code == 200
    assert field in response.context_data["form"].errors
    spy.assert_not_called()
    assert "csrfmiddlewaretoken" in response.content.decode()


@pytest.mark.parametrize("kind", ["equal", "outside", "missing_offer", "duplicate", "full"])
def test_book_view_revalidation_errors_are_safe_and_preserve_records(presentation_scene, kind):
    scene = presentation_scene
    actor, data, offer_id = scene.outsider, valid_booking_post(scene), scene.offer.pk
    if kind == "equal":
        data["alighting_point_id"] = data["boarding_point_id"]
    elif kind == "outside":
        outsider_point = RoutePoint.objects.create(code="fora-sintetico", name="Fora Sintético")
        data["boarding_point_id"] = str(outsider_point.pk)
    elif kind == "missing_offer":
        offer_id = 999999999
    elif kind == "duplicate":
        actor = scene.passenger
    else:
        RideOffer.objects.filter(pk=scene.offer.pk).update(seats=2)
    before = list(booking_model().objects.order_by("pk").values())
    response = reserve_view(scene, user=actor, data=data, offer_id=offer_id)
    assert response.status_code == 200 and response.context_data["form"].errors
    assert list(booking_model().objects.order_by("pk").values()) == before
    html = response.content.decode()
    assert scene.driver.email not in html
    # The error page may display the viewer's other confirmed booking, never an unrelated one.
    expected = scene.first_booking if actor.pk == scene.passenger.pk else scene.external_booking
    assert [dto.booking_id for dto in response.context_data["bookings"]] == [expected.pk]
    if actor.pk == scene.passenger.pk:
        assert "PLACA-EXTERNA" not in html
    else:
        assert scene.driver.full_name not in html and scene.offer.vehicle_plate not in html
    if kind in ("equal", "outside"):
        target = "alighting_point_id" if kind == "equal" else "boarding_point_id"
        assert target in response.context_data["form"].errors
    if kind == "full":
        assert "Não há vagas disponíveis" in html


@pytest.mark.parametrize("view_name", ["BookRideView", "MyBookingsView"])
@pytest.mark.parametrize("kind", ["anonymous", "pending", "disabled", "driver"])
def test_booking_views_authorize_without_middleware(presentation_scene, view_name, kind):
    from django.contrib.auth.models import AnonymousUser
    from django.core.exceptions import PermissionDenied
    from rides import views
    scene = presentation_scene
    user = scene.driver if kind == "driver" else scene.outsider
    if kind == "anonymous":
        user = AnonymousUser()
    elif kind == "pending":
        user.academic_status = "PENDENTE"
    elif kind == "disabled":
        user.is_active = False
    request = prepared_request(
        "post" if view_name == "BookRideView" else "get", user, valid_booking_post(scene))
    view = getattr(views, view_name).as_view()
    kwargs = {"offer_id": scene.offer.pk} if view_name == "BookRideView" else {}
    if kind == "anonymous":
        assert view(request, **kwargs).status_code == 302
    elif kind == "driver" and view_name == "MyBookingsView":
        assert view(request, **kwargs).status_code == 200
    else:
        with pytest.raises(PermissionDenied):
            view(request, **kwargs)


@pytest.mark.parametrize("view_name,method", [("BookRideView", "get"), ("MyBookingsView", "post")])
def test_booking_views_methods_do_not_write(presentation_scene, view_name, method):
    from rides import views
    scene = presentation_scene
    before = booking_model().objects.count()
    request = prepared_request(method, scene.outsider)
    kwargs = {"offer_id": scene.offer.pk} if view_name == "BookRideView" else {}
    response = getattr(views, view_name).as_view()(request, **kwargs)
    assert response.status_code == 405 and booking_model().objects.count() == before


def test_book_view_csrf_middleware_rejects_missing_token_before_write(presentation_scene):
    from django.middleware.csrf import CsrfViewMiddleware
    from rides import views
    scene = presentation_scene
    request = prepared_request("post", scene.outsider, valid_booking_post(scene))
    before = booking_model().objects.count()
    refusal = CsrfViewMiddleware(lambda request: None).process_view(
        request, views.BookRideView.as_view(), (), {"offer_id": scene.offer.pk})
    assert refusal.status_code == 403 and booking_model().objects.count() == before


# Feature 004/T005 local — roadmap T023; URLs reais e middleware completo.
def booking_http_url(scene):
    return f"/caronas/{scene.offer.pk}/reservar/"


def test_booking_http_named_routes_and_existing_routes(presentation_scene):
    from django.urls import resolve, reverse
    from rides import views
    scene = presentation_scene
    assert reverse("rides:book", kwargs={"offer_id": scene.offer.pk}) == booking_http_url(scene)
    assert reverse("rides:my_bookings") == "/caronas/minhas-reservas/"
    assert resolve(booking_http_url(scene)).func.view_class is views.BookRideView
    assert resolve("/caronas/minhas-reservas/").func.view_class is views.MyBookingsView
    assert reverse("rides:search") == "/caronas/buscar/"
    assert reverse("rides:offer-create") == "/caronas/oferecer/"
    assert reverse("rides:my-offers") == "/caronas/minhas-ofertas/"
    assert reverse("caronas") == "/caronas/"


def test_booking_http_real_login_csrf_search_reserve_and_private_list(presentation_scene):
    from django.conf import settings
    from django.test import Client
    scene = presentation_scene
    scene.outsider.set_password("Senha-sintetica-2026!")
    scene.outsider.save(update_fields=["password", "updated_at"])
    client = Client(enforce_csrf_checks=True)
    assert client.get("/accounts/login/").status_code == 200
    token = client.cookies[settings.CSRF_COOKIE_NAME].value
    login = client.post("/accounts/login/", {
        "email": scene.outsider.email, "password": "Senha-sintetica-2026!",
        "csrfmiddlewaretoken": token})
    assert login.status_code == 302 and login.url == "/accounts/profile/"
    query = {"boarding_id": scene.points[0].pk, "alighting_id": scene.points[-1].pk,
             "desired_at": scene.offer.departure_at.isoformat()}
    search = client.get("/caronas/buscar/", query)
    assert search.status_code == 200
    assert search.context["results"][0].available_seats == 1
    assert scene.driver.full_name not in search.content.decode()
    assert scene.offer.vehicle_plate not in search.content.decode()

    token = client.cookies[settings.CSRF_COOKIE_NAME].value
    data = {**valid_booking_post(scene), "csrfmiddlewaretoken": token,
            "passenger_id": str(scene.second.pk), "status": "CANCELADA",
            "next": "https://example.invalid/"}
    response = client.post(booking_http_url(scene), data, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [("/caronas/minhas-reservas/", 302)]
    created = booking_model().objects.get(offer=scene.offer, passenger=scene.outsider)
    assert created.status == "CONFIRMADA"
    assert [dto.booking_id for dto in response.context["bookings"]] == [
        created.pk, scene.external_booking.pk]
    html = response.content.decode()
    assert "Reserva confirmada com sucesso." in html
    assert scene.driver.full_name in html and scene.offer.vehicle_plate in html
    for value in (scene.passenger.full_name, scene.second.full_name, scene.driver.email,
                  scene.outsider.email, scene.passenger.email, "application/json"):
        assert value not in html
    current = client.get("/caronas/buscar/", query)
    assert current.context["results"][0].available_seats == 0
    assert "Vagas esgotadas." in current.content.decode()
    repeated = client.post(booking_http_url(scene), data)
    assert repeated.status_code == 200
    assert "Você já possui reserva confirmada" in repeated.content.decode()
    assert booking_model().objects.filter(offer=scene.offer, passenger=scene.outsider).count() == 1


@pytest.mark.parametrize("route", ["book", "mine"])
@pytest.mark.parametrize("kind", ["visitor", "pending", "disabled", "driver", "passenger"])
def test_booking_http_access_matrix_with_real_middleware(presentation_scene, route, kind):
    from django.test import Client
    scene = presentation_scene
    client = Client()
    actor = scene.driver if kind == "driver" else scene.outsider
    if kind != "visitor":
        client.force_login(actor)
    if kind == "pending":
        get_user_model().objects.filter(pk=actor.pk).update(academic_status="PENDENTE")
    if kind == "disabled":
        get_user_model().objects.filter(pk=actor.pk).update(is_active=False)
    before = booking_model().objects.count()
    url = booking_http_url(scene) if route == "book" else "/caronas/minhas-reservas/"
    response = client.post(url, valid_booking_post(scene)) if route == "book" else client.get(url)
    if kind in ("visitor", "disabled"):
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=" + url
    elif kind == "pending":
        assert response.status_code == 302 and response.url == "/accounts/activation/"
    elif route == "book" and kind == "driver":
        assert response.status_code == 403
    elif route == "book":
        assert response.status_code == 302 and response.url == "/caronas/minhas-reservas/"
    else:
        assert response.status_code == 200
    assert booking_model().objects.count() == before + int(route == "book" and kind == "passenger")


@pytest.mark.parametrize("with_cookie", [False, True])
def test_booking_http_missing_or_invalid_csrf_never_creates(presentation_scene, with_cookie):
    from django.test import Client
    scene = presentation_scene
    client = Client(enforce_csrf_checks=True)
    if with_cookie:
        client.get("/accounts/login/")
    client.force_login(scene.outsider)
    before = booking_model().objects.count()
    payload = valid_booking_post(scene)
    if with_cookie:
        payload["csrfmiddlewaretoken"] = "token-invalido"
    response = client.post(booking_http_url(scene), payload)
    assert response.status_code == 403
    assert booking_model().objects.count() == before


@pytest.mark.parametrize("route,method", [
    ("book", "get"), ("book", "put"), ("book", "patch"), ("book", "delete"),
    ("mine", "post"), ("mine", "put"), ("mine", "patch"), ("mine", "delete"),
])
def test_booking_http_methods_are_restricted(presentation_scene, route, method):
    from django.test import Client
    scene = presentation_scene
    client = Client()
    client.force_login(scene.outsider)
    before = list(booking_model().objects.order_by("pk").values())
    url = booking_http_url(scene) if route == "book" else "/caronas/minhas-reservas/"
    response = getattr(client, method)(url, data=valid_booking_post(scene))
    assert response.status_code == 405
    assert list(booking_model().objects.order_by("pk").values()) == before


@pytest.mark.parametrize("kind", ["missing", "unknown_point", "equal", "reversed", "missing_offer", "duplicate", "full"])
def test_booking_http_refusals_leave_domain_unchanged(presentation_scene, kind):
    from django.test import Client
    scene = presentation_scene
    data = valid_booking_post(scene)
    actor, url = scene.outsider, booking_http_url(scene)
    if kind == "missing":
        data.pop("alighting_point_id")
    elif kind == "unknown_point":
        data["boarding_point_id"] = "999999999"
    elif kind == "equal":
        data["alighting_point_id"] = data["boarding_point_id"]
    elif kind == "reversed":
        data["boarding_point_id"], data["alighting_point_id"] = (
            data["alighting_point_id"], data["boarding_point_id"])
    elif kind == "missing_offer":
        url = "/caronas/999999999/reservar/"
    elif kind == "duplicate":
        actor = scene.passenger
    else:
        RideOffer.objects.filter(pk=scene.offer.pk).update(seats=2)
    client = Client()
    client.force_login(actor)
    models = (booking_model(), RideOffer, Waypoint, RoutePoint, get_user_model())
    before = tuple(list(model.objects.order_by("pk").values()) for model in models)
    response = client.post(url, data)
    assert response.status_code == 200
    assert response.context["form"].errors
    assert tuple(list(model.objects.order_by("pk").values()) for model in models) == before


@pytest.mark.parametrize("who", ["passenger", "driver", "outsider", "other_driver"])
def test_booking_http_private_lists_ignore_third_party_identifiers(presentation_scene, who):
    from django.test import Client
    scene = presentation_scene
    actor = getattr(scene, who)
    client = Client()
    client.force_login(actor)
    response = client.get("/caronas/minhas-reservas/", {
        "user_id": scene.second.pk, "passenger_id": scene.outsider.pk,
        "booking_id": scene.first_booking.pk, "offer_id": scene.offer.pk})
    assert response.status_code == 200
    expected = {"passenger": [scene.first_booking.pk],
                "driver": [scene.first_booking.pk, scene.second_booking.pk],
                "outsider": [scene.external_booking.pk],
                "other_driver": [scene.external_booking.pk]}[who]
    assert [dto.booking_id for dto in response.context["bookings"]] == expected
    html = response.content.decode()
    for person in (scene.passenger, scene.second, scene.outsider, scene.driver, scene.other_driver):
        assert person.email not in html
    if who in ("outsider", "other_driver"):
        assert scene.driver.full_name not in html and scene.offer.vehicle_plate not in html
    if who == "passenger":
        assert scene.second.full_name not in html and "PLACA-EXTERNA" not in html


def test_booking_http_cancelled_records_are_redacted_after_new_request(presentation_scene):
    from django.test import Client
    scene = presentation_scene
    client = Client()
    client.force_login(scene.passenger)
    first = client.get("/caronas/minhas-reservas/")
    assert first.status_code == 200
    assert scene.driver.full_name in first.content.decode()
    booking_model().objects.filter(pk=scene.first_booking.pk).update(status="CANCELADA")
    current = client.get("/caronas/minhas-reservas/")
    assert current.status_code == 200
    assert current.context["bookings"][0].vehicle_plate is None
    html = current.content.decode()
    assert scene.driver.full_name not in html and scene.offer.vehicle_plate not in html
    assert scene.driver.display_name in html


def test_booking_http_get_list_does_not_write_domain(presentation_scene):
    from django.test import Client
    scene = presentation_scene
    client = Client()
    client.force_login(scene.passenger)
    models = (booking_model(), RideOffer, Waypoint, RoutePoint, get_user_model())
    before = tuple(list(model.objects.order_by("pk").values()) for model in models)
    response = client.get("/caronas/minhas-reservas/")
    assert response.status_code == 200
    assert tuple(list(model.objects.order_by("pk").values()) for model in models) == before
