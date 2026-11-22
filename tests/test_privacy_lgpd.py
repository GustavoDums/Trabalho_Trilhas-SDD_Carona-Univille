"""Feature 001 / T010 — REQ-002 e REQ-003, apenas dados sintéticos."""

import pytest
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_login_get(client):
    response = client.get(reverse("accounts:login"))
    assert response.status_code == 200
    assert 'name="email"' in response.content.decode()
    assert 'type="password"' in response.content.decode()


@pytest.mark.parametrize("status,destination", [("PENDENTE", "/accounts/activation/"),
                                               ("ATIVA", "/accounts/profile/")])
@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
def test_manual_login_routes_by_academic_status(client, academic_user_factory, status, destination, role):
    user = academic_user_factory(role=role)
    if status == "ATIVA":
        user.academic_status = status
        user.save()
    response = client.post(reverse("accounts:login"), {
        "email": user.email, "password": "Senha-sintetica-2026!", "next": "https://example.org/",
    })
    assert response.status_code == 302 and response.url == destination
    assert client.session["_auth_user_id"] == str(user.pk)


@pytest.mark.parametrize("kind", ["wrong_password", "missing_user", "disabled"])
def test_invalid_login_is_generic(client, academic_user_factory, kind):
    user = academic_user_factory()
    if kind == "disabled":
        user.is_active = False
        user.save()
    email = "ausente.sintetico@univille.br" if kind == "missing_user" else user.email
    password = "Senha-errada!2026" if kind == "wrong_password" else "Senha-sintetica-2026!"
    response = client.post(reverse("accounts:login"), {"email": email, "password": password})
    assert response.status_code == 200
    assert list(response.context["form"].non_field_errors()) == ["E-mail ou senha incorretos."]
    assert "_auth_user_id" not in client.session
    assert password not in response.content.decode()


@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
def test_profile_contains_only_own_data_and_abbreviated_preview(client, academic_user_factory, role):
    user = academic_user_factory(full_name="Lucas Aluno", role=role)
    user.academic_status = "ATIVA"
    user.save()
    other = academic_user_factory(full_name="Outra Pessoa")
    client.force_login(user)
    response = client.get(reverse("accounts:profile"), {"user_id": other.pk, "email": other.email})
    assert response.status_code == 200
    html = response.content.decode()
    assert user.full_name in html and "Lucas A." in html
    assert user.get_role_display() in html and "Ativo" in html
    assert user.email not in html and other.email not in html
    assert other.full_name not in html
    assert "confidencial" in html


def test_profile_is_not_public_or_accessible_to_pending(client, pending_client):
    url = reverse("accounts:profile")
    response = client.get(url)
    assert response.status_code == 302 and response.url.startswith("/accounts/login/")
    response = pending_client.get(url)
    assert response.status_code == 302 and response.url == "/accounts/activation/"


def test_login_csrf(academic_user_factory):
    user = academic_user_factory()
    client = Client(enforce_csrf_checks=True)
    url = reverse("accounts:login")
    data = {"email": user.email, "password": "Senha-sintetica-2026!"}
    assert client.post(url, data).status_code == 403
    assert client.get(url).status_code == 200
    data["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
    assert client.post(url, data).status_code == 302
    assert client.session["_auth_user_id"] == str(user.pk)


def test_authenticated_active_login_does_not_loop(active_client):
    response = active_client.get(reverse("accounts:login"))
    assert response.status_code == 302 and response.url == "/accounts/profile/"


def test_login_requires_credentials(client):
    response = client.post(reverse("accounts:login"), {})
    assert response.status_code == 200
    assert set(response.context["form"].errors) == {"email", "password"}
    assert "_auth_user_id" not in client.session


@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
def test_registration_manual_login_activation_profile_flow(client, role):
    email = "lucas.aluno@univille.br"
    password = "Ficticia!Rota-2026#"
    response = client.post(reverse("accounts:register"), {
        "full_name": "Lucas Aluno", "email": email, "role": role,
        "password": password, "password_confirm": password,
    }, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [("/accounts/login/", 302)]
    assert "_auth_user_id" not in client.session
    response = client.post(reverse("accounts:login"), {"email": email, "password": password}, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [("/accounts/activation/", 302)]
    response = client.post(reverse("accounts:activation"), follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [("/accounts/profile/", 302)]
    assert "Lucas A." in response.content.decode()
    assert email not in response.content.decode()
