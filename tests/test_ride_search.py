"""Feature 003/T003 local — roadmap T018; formulários e HTML sem endpoint."""
from dataclasses import replace
from datetime import datetime, timezone as dt_timezone
from html.parser import HTMLParser

import pytest
from django import forms
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.utils import timezone

from rides import forms as ride_forms
from rides.models import RoutePoint
from rides.services.matching_service import SearchQuery, SearchResult


@pytest.fixture
def search_data(db):
    points = list(RoutePoint.objects.order_by("pk"))
    return {"boarding_id": str(points[0].pk), "alighting_id": str(points[1].pk),
            "desired_at": "2030-01-03T08:15:42"}


def make_form(data=None):
    return ride_forms.RideSearchForm(data=data)


def result():
    return SearchResult(
        offer_id=7, driver_display_name="Pessoa S.",
        itinerary=("Origem Sintética", "Parada Sintética", "Destino Sintético"),
        departure_at=datetime(2030, 1, 3, 11, 15, 42, tzinfo=dt_timezone.utc),
        seats=3, available_seats=3, vehicle_model="Veículo Sintético", vehicle_color="Azul")


def page(form, *, searched=False, results=()):
    request = RequestFactory().get("/caronas/buscar/", data=form.data)
    return render_to_string("rides/search.html",
                            {"form": form, "searched": searched, "results": results}, request=request)


class ParsedForm(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


@pytest.mark.django_db
def test_search_form_contract(search_data):
    form = make_form(search_data)
    assert set(form.fields) == {"boarding_id", "alighting_id", "desired_at"}
    assert isinstance(form.fields["boarding_id"], forms.ModelChoiceField)
    assert isinstance(form.fields["alighting_id"], forms.ModelChoiceField)
    assert all(field.required for field in form.fields.values())
    with timezone.override("UTC"):
        assert form.is_valid(), form.errors
    assert form.cleaned_data["desired_at"] == datetime(2030, 1, 3, 11, 15, 42, tzinfo=dt_timezone.utc)
    q = SearchQuery(
        boarding_id=form.cleaned_data["boarding_id"].pk,
        alighting_id=form.cleaned_data["alighting_id"].pk,
        desired_at=form.cleaned_data["desired_at"])
    assert q.boarding_id != q.alighting_id


@pytest.mark.parametrize("field", ["boarding_id", "alighting_id", "desired_at"])
@pytest.mark.django_db
def test_missing_fields_are_specific(search_data, field):
    search_data.pop(field)
    form = make_form(search_data)
    assert not form.is_valid()
    assert field in form.errors


@pytest.mark.parametrize("field", ["boarding_id", "alighting_id"])
@pytest.mark.parametrize("invalid", ["", "999999999", "1.5", "abc", "-1", "0"])
@pytest.mark.django_db
def test_invalid_catalog_is_specific(search_data, field, invalid):
    search_data[field] = invalid
    form = make_form(search_data)
    assert not form.is_valid() and field in form.errors


@pytest.mark.django_db
def test_equal_points(search_data):
    search_data["alighting_id"] = search_data["boarding_id"]
    form = make_form(search_data)
    assert not form.is_valid()
    assert "alighting_id" in form.errors


@pytest.mark.parametrize("invalid", ["", "nunca", "2030-02-30T10:00", "2030-01-03T25:00"])
@pytest.mark.django_db
def test_invalid_datetime(search_data, invalid):
    search_data["desired_at"] = invalid
    form = make_form(search_data)
    assert not form.is_valid() and "desired_at" in form.errors


@pytest.mark.django_db
def test_past_desired_and_extra_parameters_do_not_change_contract(search_data):
    search_data.update(desired_at="2000-01-01T08:00", tolerance="999", window="900",
                       driver="123", user_id="456")
    form = make_form(search_data)
    assert form.is_valid(), form.errors
    assert set(form.cleaned_data) == {"boarding_id", "alighting_id", "desired_at"}


@pytest.mark.django_db
def test_input_offset_and_seconds_are_preserved(search_data):
    search_data["desired_at"] = "2030-01-03T08:15:42-03:00"
    form = make_form(search_data)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["desired_at"] == datetime(2030, 1, 3, 11, 15, 42, tzinfo=dt_timezone.utc)


@pytest.mark.django_db
def test_initial_empty_and_invalid_are_distinct(search_data):
    initial = page(make_form())
    assert "Nenhuma oferta compatível" not in initial
    assert 'data-offer-id=' not in initial
    assert "Informe os filtros" in initial
    form = make_form(search_data)
    assert form.is_valid()
    empty = page(form, searched=True)
    assert "Nenhuma oferta compatível com os filtros informados." in empty
    invalid = make_form({"boarding_id": search_data["boarding_id"], "desired_at": "inválido"})
    assert not invalid.is_valid()
    error_html = page(invalid, searched=True)
    assert "Corrija os campos" in error_html
    assert "Nenhuma oferta compatível" not in error_html
    assert "errorlist" in error_html
    assert 'data-offer-id=' not in error_html


@pytest.mark.django_db
def test_get_form_preserves_filters_and_explains_fixed_origin_window(search_data):
    form = make_form(search_data)
    assert form.is_valid()
    html = page(form, searched=True, results=(result(),))
    tags = ParsedForm(html).tags
    assert any(t == "form" and a.get("method") == "get" for t, a in tags)
    selected = {a["value"] for t, a in tags if t == "option" and "selected" in a}
    assert {search_data["boarding_id"], search_data["alighting_id"]} <= selected
    desired = next(a for t, a in tags if t == "input" and a.get("name") == "desired_at")
    assert desired["type"] == "datetime-local" and desired["step"] == "1"
    assert desired["value"] == search_data["desired_at"]
    assert "America/Sao_Paulo" in html
    assert html.count("Não representa previsão de passagem nas paradas.") >= 2
    assert "Janela fixa de ±30 minutos em relação à saída da origem." in html
    assert {a.get("name") for t, a in tags if t in {"input", "select"}} == set(form.fields)
    assert "csrfmiddlewaretoken" not in html


@pytest.mark.django_db
def test_public_cards_and_partial_escape_labels_without_secrets(search_data):
    dto = replace(result(), driver_display_name="<b>Pessoa S.</b>",
                  itinerary=("Origem <script>alert(1)</script>", "Parada & Demo", "Destino"),
                  vehicle_model="<img src=x onerror=alert(1)>")
    form = make_form(search_data)
    assert form.is_valid()
    html = page(form, searched=True, results=(dto,))
    assert "&lt;b&gt;Pessoa S.&lt;/b&gt;" in html
    assert "&lt;script&gt;" in html and "&lt;img" in html
    assert "<script>" not in html and "<img src=x" not in html
    assert html.index("Origem &lt;script") < html.index("Parada &amp; Demo") < html.index(">Destino<")
    assert 'data-offer-id="7"' in html
    assert "3 vagas disponíveis" in html and "03/01/2030 08:15:42" in html
    for secret in ("Pessoa Sintética", "motorista.sintetico@univille.br", "PRIVADA-123",
                   "vehicle_plate", "full_name", "driver_email", "application/json"):
        assert secret not in html
    text = html.lower()
    assert "reservar" not in text and "reputação" not in text and "★" not in text
    partial = render_to_string("rides/_search_result.html", {"result": result()})
    assert "Pessoa S." in partial and 'data-offer-id="7"' in partial
    assert "Não representa previsão de passagem nas paradas." in partial


@pytest.mark.django_db
def test_catalog_labels_are_names_and_escaped(search_data):
    point = RoutePoint.objects.get(pk=search_data["boarding_id"])
    point.name = "Ponto <b>Sintético</b>"
    point.save()
    html = page(make_form())
    assert "Ponto &lt;b&gt;Sintético&lt;/b&gt;" in html
    assert "RoutePoint object" not in html



# Feature 003/T004 local — roadmap T019; HTTP real sobre o serviço existente.
@pytest.fixture
def http_scene(academic_user_factory, monkeypatch):
    from datetime import timedelta
    from types import SimpleNamespace
    from django.test import Client
    from rides.models import RideOffer, Waypoint

    now = datetime(2030, 1, 2, 12, tzinfo=dt_timezone.utc)
    departure = now + timedelta(days=1)
    monkeypatch.setattr(timezone, "now", lambda: now)

    def user(role, name):
        account = academic_user_factory(role=role, full_name=name, password=None)
        account.academic_status = "ATIVA"
        account.save(update_fields=["academic_status", "updated_at"])
        return account

    passenger = user("PASSAGEIRO", "Passageiro Sintético")
    driver = user("MOTORISTA", "Motorista Sintético")
    other_driver = user("MOTORISTA", "Condutor Fictício")
    catalog = {point.code: point for point in RoutePoint.objects.all()}
    points = [catalog[code] for code in
              ("terminal-norte", "campus-univille", "bairro-america", "terminal-central")]

    def offer(author, at, with_stops=False):
        value = RideOffer.objects.create(
            driver=author, origin=points[0], destination=points[-1], departure_at=at,
            seats=3, vehicle_model="Veículo Sintético", vehicle_color="Azul",
            vehicle_plate="PRIVADA-123")
        if with_stops:
            Waypoint.objects.create(offer=value, point=points[2], position=2)
            Waypoint.objects.create(offer=value, point=points[1], position=1)
        return value

    first = offer(driver, departure, with_stops=True)
    second = offer(other_driver, departure-timedelta(minutes=15))
    client = Client(enforce_csrf_checks=True)
    client.force_login(passenger)
    data = {"boarding_id": str(points[0].pk), "alighting_id": str(points[-1].pk),
            "desired_at": departure.isoformat()}
    return SimpleNamespace(client=client, passenger=passenger, driver=driver,
                           other_driver=other_driver, first=first, second=second,
                           points=points, data=data, now=now, departure=departure)


def http_search(scene, data=None):
    return scene.client.get("/caronas/buscar/", data=data)


def test_http_named_route():
    from django.urls import reverse
    assert reverse("rides:search") == "/caronas/buscar/"


@pytest.mark.django_db
def test_http_initial_does_not_query_matching(http_scene, monkeypatch):
    from unittest.mock import Mock
    from rides.services.matching_service import MatchingService
    spy = Mock(return_value=())
    monkeypatch.setattr(MatchingService, "search", spy)
    response = http_search(http_scene)
    assert response.status_code == 200
    assert not response.context["searched"]
    assert not response.context["form"].is_bound
    assert response.context["results"] == ()
    spy.assert_not_called()
    assert "Nenhuma oferta compatível" not in response.content.decode()


@pytest.mark.parametrize("kind,status", [
    ("visitor", 302), ("pending", 302), ("driver", 403), ("disabled", 302),
    ("passenger", 200),
])
@pytest.mark.django_db
def test_http_access_matrix(http_scene, kind, status):
    from django.contrib.auth import get_user_model
    from django.test import Client
    client = Client()
    if kind == "driver":
        client.force_login(http_scene.driver)
    elif kind != "visitor":
        client.force_login(http_scene.passenger)
        changes = {"academic_status": "PENDENTE"} if kind == "pending" else {"is_active": False}
        if kind != "passenger":
            get_user_model().objects.filter(pk=http_scene.passenger.pk).update(**changes)
    response = client.get("/caronas/buscar/")
    assert response.status_code == status
    if kind in ("visitor", "disabled"):
        assert response.url == "/accounts/login/?next=/caronas/buscar/"
    if kind == "pending":
        assert response.url == "/accounts/activation/"


@pytest.mark.parametrize("field,value", [
    ("boarding_id", ""), ("boarding_id", "999999999"), ("boarding_id", "1.5"),
    ("alighting_id", ""), ("alighting_id", "999999999"), ("desired_at", "inválido"),
    ("desired_at", ""),
])
@pytest.mark.django_db
def test_http_invalid_input_does_not_call_matching(http_scene, monkeypatch, field, value):
    from unittest.mock import Mock
    from rides.services.matching_service import MatchingService
    spy = Mock(return_value=())
    monkeypatch.setattr(MatchingService, "search", spy)
    data = dict(http_scene.data, **{field: value})
    response = http_search(http_scene, data)
    assert response.status_code == 200
    assert response.context["searched"]
    assert field in response.context["form"].errors
    assert response.context["results"] == ()
    spy.assert_not_called()
    assert "Nenhuma oferta compatível" not in response.content.decode()


@pytest.mark.django_db
def test_http_equal_points_and_extra_only_are_invalid(http_scene):
    response = http_search(http_scene, dict(http_scene.data,
                                           alighting_id=http_scene.data["boarding_id"]))
    assert response.status_code == 200
    assert "alighting_id" in response.context["form"].errors
    response = http_search(http_scene, {"tolerance": "999"})
    assert response.status_code == 200 and response.context["searched"]
    assert set(response.context["form"].errors) == {"boarding_id", "alighting_id", "desired_at"}


@pytest.mark.django_db
def test_http_valid_query_converted_and_session_user_forwarded(http_scene, monkeypatch):
    from unittest.mock import Mock
    from rides.services.matching_service import MatchingService
    spy = Mock(return_value=(result(),))
    monkeypatch.setattr(MatchingService, "search", spy)
    response = http_search(http_scene, http_scene.data)
    assert response.status_code == 200
    spy.assert_called_once()
    assert spy.call_args.kwargs["passenger"].pk == http_scene.passenger.pk
    q = spy.call_args.kwargs["query"]
    assert isinstance(q, SearchQuery)
    assert q.boarding_id == http_scene.points[0].pk
    assert q.alighting_id == http_scene.points[-1].pk
    assert q.desired_at == http_scene.departure
    assert response.context["results"] == (result(),)


@pytest.mark.django_db
def test_http_results_order_unique_private_and_read_only(http_scene):
    from django.contrib.auth import get_user_model
    from rides.models import RideOffer, Waypoint

    def snapshot():
        return (list(RideOffer.objects.order_by("pk").values()),
                list(Waypoint.objects.order_by("pk").values()),
                list(RoutePoint.objects.order_by("pk").values()),
                list(get_user_model().objects.order_by("pk").values()))

    before = snapshot()
    response = http_search(http_scene, http_scene.data)
    assert response.status_code == 200
    results = response.context["results"]
    assert isinstance(results, tuple) and all(isinstance(item, SearchResult) for item in results)
    assert [item.offer_id for item in results] == [http_scene.second.pk, http_scene.first.pk]
    assert results[1].itinerary == tuple(point.name for point in http_scene.points)
    assert snapshot() == before
    html = response.content.decode()
    for user in (http_scene.driver, http_scene.other_driver):
        assert user.display_name in html
        assert user.full_name not in html and user.email not in html
    assert "PRIVADA-123" not in html
    assert "application/json" not in html and "reservar" not in html.lower()
    assert "Não representa previsão de passagem nas paradas." in html


@pytest.mark.django_db
def test_http_intermediate_points_empty_and_filters_preserved(http_scene):
    data = dict(http_scene.data, boarding_id=str(http_scene.points[1].pk),
                alighting_id=str(http_scene.points[2].pk))
    response = http_search(http_scene, data)
    assert response.status_code == 200
    assert [item.offer_id for item in response.context["results"]] == [http_scene.first.pk]
    inverted = dict(data, boarding_id=data["alighting_id"], alighting_id=data["boarding_id"])
    response = http_search(http_scene, inverted)
    assert response.status_code == 200 and response.context["results"] == ()
    assert response.context["form"].data.dict() == inverted
    assert "Nenhuma oferta compatível com os filtros informados." in response.content.decode()


@pytest.mark.parametrize("change", ["pending", "disabled", "wrong_role", "past", "now", "outside"])
@pytest.mark.django_db
def test_http_excludes_ineligible_offers_on_next_search(http_scene, change):
    from datetime import timedelta
    from django.contrib.auth import get_user_model
    from rides.models import RideOffer

    assert http_search(http_scene, http_scene.data).status_code == 200
    if change in ("pending", "disabled", "wrong_role"):
        values = {"pending": {"academic_status": "PENDENTE"}, "disabled": {"is_active": False},
                  "wrong_role": {"role": "PASSAGEIRO"}}[change]
        get_user_model().objects.filter(pk=http_scene.driver.pk).update(**values)
    else:
        at = {"past": http_scene.now-timedelta(seconds=1), "now": http_scene.now,
              "outside": http_scene.departure+timedelta(minutes=30, seconds=1)}[change]
        RideOffer.objects.filter(pk=http_scene.first.pk).update(departure_at=at)
    response = http_search(http_scene, http_scene.data)
    assert response.status_code == 200
    assert [item.offer_id for item in response.context["results"]] == [http_scene.second.pk]


@pytest.mark.django_db
def test_http_extra_parameters_cannot_relax_window_or_choose_user(http_scene):
    from datetime import timedelta
    from rides.models import RideOffer
    RideOffer.objects.filter(pk=http_scene.first.pk).update(
        departure_at=http_scene.departure+timedelta(minutes=30, seconds=1))
    data = dict(http_scene.data, tolerance="999", window="999", user_id=str(http_scene.driver.pk),
                driver=str(http_scene.driver.pk), page="999")
    response = http_search(http_scene, data)
    assert response.status_code == 200
    assert [item.offer_id for item in response.context["results"]] == [http_scene.second.pk]
    assert set(response.context["form"].cleaned_data) == {"boarding_id", "alighting_id", "desired_at"}


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
@pytest.mark.django_db
def test_http_write_methods_405_and_no_matching(http_scene, monkeypatch, method):
    from unittest.mock import Mock
    from rides.services.matching_service import MatchingService
    spy = Mock(return_value=())
    monkeypatch.setattr(MatchingService, "search", spy)
    # Default Django test client bypasses CSRF here to isolate the method contract.
    from django.test import Client
    client = Client()
    client.force_login(http_scene.passenger)
    response = getattr(client, method)("/caronas/buscar/", data=http_scene.data)
    assert response.status_code == 405
    spy.assert_not_called()


@pytest.mark.parametrize("error", ["field", "general", "permission"])
@pytest.mark.django_db
def test_http_service_revalidation_errors_are_safe(http_scene, monkeypatch, error):
    from django.core.exceptions import PermissionDenied, ValidationError
    from rides.services.matching_service import MatchingService
    from unittest.mock import Mock

    failures = {"field": ValidationError({"boarding_id": "Selecione um ponto existente do catálogo."}),
                "general": ValidationError("Consulta inválida."),
                "permission": PermissionDenied("Acesso recusado.")}
    monkeypatch.setattr(MatchingService, "search", Mock(side_effect=failures[error]))
    response = http_search(http_scene, http_scene.data)
    assert response.status_code == (403 if error == "permission" else 200)
    assert "PRIVADA-123" not in response.content.decode()
    if error != "permission":
        assert response.context["results"] == ()
        assert response.context["form"].errors


@pytest.mark.parametrize("kind", ["driver", "pending", "disabled"])
@pytest.mark.django_db
def test_passenger_mixin_rejects_without_middleware(http_scene, kind):
    from django.core.exceptions import PermissionDenied
    from rides import views
    user = http_scene.driver if kind == "driver" else http_scene.passenger
    if kind == "pending":
        user.academic_status = "PENDENTE"
    if kind == "disabled":
        user.is_active = False
    request = RequestFactory().get("/caronas/buscar/")
    request.user = user
    with pytest.raises(PermissionDenied):
        views.RideSearchView.as_view()(request)


@pytest.mark.django_db
def test_existing_routes_preserved(http_scene):
    from django.urls import reverse
    assert reverse("rides:offer-create") == "/caronas/oferecer/"
    assert reverse("rides:my-offers") == "/caronas/minhas-ofertas/"
    assert reverse("caronas") == "/caronas/"
    http_scene.client.force_login(http_scene.driver)
    for url in ("/caronas/oferecer/", "/caronas/minhas-ofertas/", "/caronas/"):
        assert http_scene.client.get(url).status_code == 200


# Feature 004/T006 local — disponibilidade pública, REQ-006/REQ-003/REQ-017.
@pytest.fixture
def reservation_actor(academic_user_factory):
    def create():
        user = academic_user_factory(password=None, full_name="Reserva Sintética")
        user.academic_status = "ATIVA"
        user.save(update_fields=["academic_status", "updated_at"])
        return user
    return create


def book_for_search(scene, actor, *, offer=None, boarding=None, alighting=None):
    from rides.services.booking_service import BookingService
    return BookingService.create_booking(
        passenger=actor, offer_id=(offer or scene.first).pk,
        boarding_point_id=(boarding or scene.points[0]).pk,
        alighting_point_id=(alighting or scene.points[-1]).pk)


def public_card(response, offer_id):
    return response.content.decode().split(
        f'<article data-offer-id="{offer_id}">', 1)[1].split("</article>", 1)[0]


@pytest.mark.django_db
def test_availability_follows_confirmations_to_exhaustion(http_scene, reservation_actor):
    from rides.models import RideOffer
    expected_order = [http_scene.second.pk, http_scene.first.pk]
    for expected in (3, 2, 1, 0):
        response = http_search(http_scene, http_scene.data)
        assert response.status_code == 200
        results = response.context["results"]
        assert [item.offer_id for item in results] == expected_order
        first = results[1]
        assert first.seats == 3 and first.available_seats == expected
        assert results[0].available_seats == 3
        card = public_card(response, http_scene.first.pk)
        if expected == 1:
            assert "1 vaga disponível" in card
        else:
            assert f"{expected} vagas disponíveis" in card
        assert ("Vagas esgotadas." in card) is (expected == 0)
        assert "vagas ofertadas" not in card
        if expected:
            book_for_search(http_scene, reservation_actor())
    assert RideOffer.objects.get(pk=http_scene.first.pk).seats == 3


@pytest.mark.django_db
def test_availability_cancelled_history_is_not_counted(http_scene, reservation_actor):
    from rides.models import RideBooking
    actor = reservation_actor()
    RideBooking.objects.create(
        offer=http_scene.first, passenger=actor,
        boarding_point=http_scene.points[0], alighting_point=http_scene.points[-1],
        status="CANCELADA")
    book_for_search(http_scene, actor)
    response = http_search(http_scene, http_scene.data)
    by_id = {dto.offer_id: dto for dto in response.context["results"]}
    assert by_id[http_scene.first.pk].available_seats == 2
    assert by_id[http_scene.second.pk].available_seats == 3


@pytest.mark.django_db
def test_availability_counts_whole_offer_without_segment_reuse(http_scene, reservation_actor):
    book_for_search(http_scene, reservation_actor(), alighting=http_scene.points[1])
    book_for_search(http_scene, reservation_actor(), boarding=http_scene.points[2])
    response = http_search(http_scene, dict(
        http_scene.data, boarding_id=str(http_scene.points[1].pk),
        alighting_id=str(http_scene.points[2].pk)))
    assert response.status_code == 200
    assert len(response.context["results"]) == 1
    assert response.context["results"][0].available_seats == 1


@pytest.mark.django_db
def test_availability_rollback_does_not_reduce_public_balance(http_scene, reservation_actor):
    from django.db import transaction
    actor = reservation_actor()
    with pytest.raises(RuntimeError):
        with transaction.atomic():
            book_for_search(http_scene, actor)
            raise RuntimeError("Rollback sintético")
    response = http_search(http_scene, http_scene.data)
    assert next(dto for dto in response.context["results"]
                if dto.offer_id == http_scene.first.pk).available_seats == 3


@pytest.mark.django_db
def test_availability_stale_result_never_overrides_booking_service(http_scene, reservation_actor):
    from rides.models import RideOffer, RideBooking
    from rides.services.booking_service import NoSeatsAvailable
    RideOffer.objects.filter(pk=http_scene.first.pk).update(seats=1)
    before = http_search(http_scene, http_scene.data)
    old = next(dto for dto in before.context["results"] if dto.offer_id == http_scene.first.pk)
    assert old.available_seats == 1
    book_for_search(http_scene, reservation_actor())
    with pytest.raises(NoSeatsAvailable):
        book_for_search(http_scene, http_scene.passenger)
    after = http_search(http_scene, http_scene.data)
    new = next(dto for dto in after.context["results"] if dto.offer_id == http_scene.first.pk)
    assert new.available_seats == 0
    assert old.available_seats == 1
    assert "Vagas esgotadas." in public_card(after, http_scene.first.pk)
    assert RideBooking.objects.filter(offer=http_scene.first, status="CONFIRMADA").count() == 1


@pytest.mark.django_db
def test_availability_keeps_filters_order_and_privacy_without_domain_writes(http_scene, reservation_actor):
    from dataclasses import fields
    from datetime import timedelta
    from django.contrib.auth import get_user_model
    from rides.models import RideBooking, RideOffer, Waypoint

    book_for_search(http_scene, reservation_actor())
    def snapshot():
        return tuple(list(model.objects.order_by("pk").values()) for model in
                     (RideBooking, RideOffer, Waypoint, RoutePoint, get_user_model()))
    before = snapshot()
    response = http_search(http_scene, dict(http_scene.data, tolerance="999", page="999"))
    assert response.status_code == 200
    results = response.context["results"]
    assert [dto.offer_id for dto in results] == [http_scene.second.pk, http_scene.first.pk]
    assert results[1].available_seats == 2
    assert {field.name for field in fields(results[1])} == {
        "offer_id", "driver_display_name", "itinerary", "departure_at", "seats",
        "available_seats", "vehicle_model", "vehicle_color"}
    html = response.content.decode()
    for secret in (http_scene.driver.full_name, http_scene.driver.email, "PRIVADA-123",
                   "Reserva Sintética", "boarding_bookings", "passenger_id", "application/json"):
        assert secret not in html
    inverted = dict(http_scene.data, boarding_id=http_scene.data["alighting_id"],
                    alighting_id=http_scene.data["boarding_id"])
    assert http_search(http_scene, inverted).context["results"] == ()
    # An available offer outside the original window must remain excluded.
    outside = dict(http_scene.data, desired_at=(http_scene.departure+timedelta(hours=2)).isoformat())
    assert http_search(http_scene, outside).context["results"] == ()
    assert snapshot() == before


@pytest.mark.django_db
def test_availability_has_no_n_plus_one_or_double_count_with_stops_and_history(
        http_scene, reservation_actor):
    from datetime import timedelta
    from django.db import connection
    from django.test.utils import CaptureQueriesContext
    from rides.models import RideBooking, RideOffer, Waypoint
    from rides.services.matching_service import MatchingService

    actor = reservation_actor()
    book_for_search(http_scene, actor)
    q = SearchQuery(boarding_id=http_scene.points[0].pk, alighting_id=http_scene.points[-1].pk,
                    desired_at=http_scene.departure)
    def search():
        with CaptureQueriesContext(connection) as captured:
            results = MatchingService.search(passenger=http_scene.passenger, query=q)
        return results, len(captured)
    small, initial_queries = search()
    assert next(dto for dto in small if dto.offer_id == http_scene.first.pk).available_seats == 2
    added_ids = []
    for offset in range(1, 5):
        offer = RideOffer.objects.create(
            driver=http_scene.driver, origin=http_scene.points[0], destination=http_scene.points[-1],
            departure_at=http_scene.departure+timedelta(minutes=offset), seats=3,
            vehicle_model="Outro Sintético", vehicle_color="Verde", vehicle_plate="SEGREDO")
        for position in (1, 2):
            Waypoint.objects.create(offer=offer, point=http_scene.points[position], position=position)
        book_for_search(http_scene, actor, offer=offer)
        for _ in range(2):
            RideBooking.objects.create(
                offer=offer, passenger=actor, boarding_point=http_scene.points[0],
                alighting_point=http_scene.points[-1], status="CANCELADA")
        added_ids.append(offer.pk)
    large, total_queries = search()
    assert total_queries == initial_queries
    assert len(large) == 6 and len({dto.offer_id for dto in large}) == 6
    assert all(dto.available_seats == 2 for dto in large if dto.offer_id in added_ids)
    assert connection.vendor == "postgresql"
