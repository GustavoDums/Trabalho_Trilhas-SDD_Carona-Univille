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
        seats=3, vehicle_model="Veículo Sintético", vehicle_color="Azul")


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
    assert "3 vagas ofertadas" in html and "03/01/2030 08:15:42" in html
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

