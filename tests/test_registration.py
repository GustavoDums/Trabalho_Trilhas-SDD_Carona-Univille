"""Feature 001 / T004 — REQ-001, REQ-002 e minimização REQ-003."""

import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.middleware.csrf import get_token

from accounts.forms import AcademicRegistrationForm
from accounts.models import AcademicUser

pytestmark = pytest.mark.django_db


def registration_data(**overrides):
    data = dict(full_name="Pessoa Sintética", email="cadastro.sintetico@univille.br",
                role="PASSAGEIRO", password="Ficticia!Rota-2026#",
                password_confirm="Ficticia!Rota-2026#")
    data.update(overrides)
    return data


@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
def test_valid_registration_form(role):
    form = AcademicRegistrationForm(data=registration_data(role=role))
    assert form.is_valid(), form.errors
    user = form.save()
    user.refresh_from_db()
    assert user.role == role
    assert user.is_pending and user.is_active
    assert user.check_password("Ficticia!Rota-2026#")
    assert user.password != "Ficticia!Rota-2026#"


@pytest.mark.parametrize("field,value", [
    ("full_name", "Pessoa"), ("full_name", "   "),
    ("email", "pessoa@example.org"), ("email", "pessoa@sub.univille.br"),
    ("email", "@univille.br"), ("email", "nome..invalido@univille.br"),
    ("role", "HIBRIDO"), ("password_confirm", "Outra-senha!2026"),
    ("password", ""), ("password_confirm", ""),
])
def test_invalid_registration_does_not_persist(field, value):
    form = AcademicRegistrationForm(data=registration_data(**{field: value}))
    assert not form.is_valid()
    assert field in form.errors
    with pytest.raises(ValueError):
        form.save()
    assert not AcademicUser.objects.exists()


@pytest.mark.parametrize("password", ["Ab!2", "123456789098765", "password", "cadastro.sintetico"])
def test_django_password_validators(password):
    form = AcademicRegistrationForm(data=registration_data(
        password=password, password_confirm=password,
    ))
    assert not form.is_valid()
    assert "password" in form.errors
    assert not AcademicUser.objects.exists()


def test_commit_false_and_untrusted_fields():
    form = AcademicRegistrationForm(data=registration_data(
        academic_status="ATIVA", is_staff=True, is_superuser=True,
    ))
    assert form.is_valid(), form.errors
    user = form.save(commit=False)
    assert user.pk is None
    assert user.is_pending and not user.is_staff and not user.is_superuser
    assert user.check_password("Ficticia!Rota-2026#")
    assert not AcademicUser.objects.exists()
    user.save()
    form.save_m2m()


def test_registration_template_and_password_privacy():
    form = AcademicRegistrationForm(data=registration_data(password_confirm="diferente"))
    assert not form.is_valid()
    request = RequestFactory().get("/accounts/register/")
    get_token(request)
    html = render_to_string("accounts/register.html", {"form": form}, request=request)
    assert 'method="post"' in html
    assert 'name="csrfmiddlewaretoken"' in html
    assert 'type="password"' in html
    for field in ("full_name", "email", "role", "password", "password_confirm"):
        assert f'name="{field}"' in html
        assert f'for="id_{field}"' in html
    assert "Ficticia!Rota-2026#" not in html
    assert "As senhas não conferem." in html
    assert set(form.fields) == {"full_name", "email", "role", "password", "password_confirm"}
