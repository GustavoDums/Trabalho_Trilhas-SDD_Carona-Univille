"""Feature 001 / T009 — REQ-002, REQ-003, FR-006.

As views de prova existem somente no URLconf de teste, sem antecipar T010/T011.
"""

import pytest
from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.urls import include, path, resolve


def protected_probe(request):
    return HttpResponse("CONTEUDO_INTERNO_SINTETICO")


def public_probe(request):
    return HttpResponse("PUBLICO_SINTETICO")


urlpatterns = [
    path("accounts/login/", public_probe),
    path("accounts/logout/", public_probe),
    path("accounts/profile/", protected_probe),
    path("caronas/", protected_probe),
    path("caronas/reservar/", protected_probe),
    path("static/test.css", public_probe),
    path("static-privado/", protected_probe),
    path("accounts/activation/extra/", protected_probe),
    path("", protected_probe),
    path("accounts/", include("accounts.urls")),
]

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def test_routes(settings):
    settings.ROOT_URLCONF = __name__


@pytest.mark.parametrize("url", ["/accounts/profile/", "/caronas/", "/caronas/reservar/", "/"])
@pytest.mark.parametrize("method", ["get", "post"])
def test_visitor_cannot_reach_protected_view(client, url, method):
    response = getattr(client, method)(url)
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/?next=")
    assert "CONTEUDO_INTERNO" not in response.content.decode()


@pytest.mark.parametrize("url", ["/accounts/profile/", "/caronas/?origem=teste", "/caronas/reservar/",
                                "/", "/accounts/register/", "/accounts/login/",
                                "/static-privado/", "/accounts/activation/extra/"])
@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
def test_pending_account_is_confined(client, academic_user_factory, url, role):
    user = academic_user_factory(role=role)
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == "/accounts/activation/"
    assert "CONTEUDO_INTERNO" not in response.content.decode()
    assert list(get_messages(response.wsgi_request))
    user.refresh_from_db()
    assert user.is_pending


def test_pending_post_cannot_reach_protected_view(pending_client):
    response = pending_client.post("/caronas/reservar/")
    assert response.status_code == 302 and response.url == "/accounts/activation/"


@pytest.mark.parametrize("url,method", [("/accounts/activation/", "get"),
                                       ("/accounts/logout/", "post"),
                                       ("/static/test.css", "get")])
def test_pending_exceptions_do_not_loop(pending_client, url, method):
    assert getattr(pending_client, method)(url).status_code == 200


@pytest.mark.parametrize("url", ["/accounts/login/", "/accounts/register/", "/static/test.css"])
def test_public_routes_remain_public(client, url):
    assert client.get(url).status_code == 200


@pytest.mark.parametrize("url", ["/accounts/profile/", "/caronas/", "/caronas/reservar/", "/"])
def test_active_account_reaches_view(active_client, url):
    response = active_client.get(url)
    assert response.status_code == 200
    assert response.content == b"CONTEUDO_INTERNO_SINTETICO"


def test_middleware_runs_after_authentication_and_messages(settings):
    entries = settings.MIDDLEWARE
    name = "accounts.middleware.AcademicStatusMiddleware"
    assert entries.index(name) > entries.index("django.contrib.auth.middleware.AuthenticationMiddleware")
    assert entries.index(name) > entries.index("django.contrib.messages.middleware.MessageMiddleware")


@pytest.fixture
def real_project_routes(settings):
    """T011 testa a rota real, sem usar as views de prova da T009."""
    settings.ROOT_URLCONF = "carona_univille.urls"


def test_caronas_placeholder_is_real_project_route(real_project_routes):
    match = resolve("/caronas/")
    assert match.view_name == "caronas"
    assert match.func.__module__ == "carona_univille.views"


def test_caronas_real_route_blocks_visitor(real_project_routes, client):
    response = client.get("/caronas/")
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/caronas/"


@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
def test_caronas_real_route_blocks_pending(real_project_routes, client, academic_user_factory, role):
    user = academic_user_factory(role=role)
    client.force_login(user)
    response = client.get("/caronas/")
    assert response.status_code == 302 and response.url == "/accounts/activation/"
    user.refresh_from_db()
    assert user.is_pending


@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
def test_caronas_real_route_allows_active(real_project_routes, client, academic_user_factory, role):
    user = academic_user_factory(role=role)
    user.academic_status = "ATIVA"
    user.save()
    client.force_login(user)
    response = client.get("/caronas/")
    assert response.status_code == 200
    assert "Área de caronas" in response.content.decode()
    assert user.email not in response.content.decode()
