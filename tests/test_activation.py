"""Feature 001 / T007 — REQ-002, validação simulada sem interface HTTP."""

import json

import pytest
from django.db import connection
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse

from accounts.models import AcademicValidationRecord
from accounts.services import AcademicValidationService

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
@pytest.mark.parametrize("email", ["joao.silva@univille.br", "mariana.motorista@univille.br",
                                  "lucas.aluno@univille.br"])
def test_eligible_account_activates_with_audit(academic_user_factory, role, email):
    user = academic_user_factory(email=email, role=role)
    before = user.password
    assert AcademicValidationService.validate(email) is True
    user.refresh_from_db()
    assert user.is_activated and user.is_active
    assert user.role == role and user.password == before
    record = user.validation_records.get()
    assert record.attempted_email == email
    assert record.simulation_result == "APROVADO"
    assert record.processed_at
    assert connection.vendor == "postgresql"


@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
@pytest.mark.parametrize("email", ["bloqueado@univille.br", "visitante.externo@univille.br"])
def test_ineligible_account_remains_pending_with_audit(academic_user_factory, role, email):
    user = academic_user_factory(email=email, role=role)
    before = user.password
    assert AcademicValidationService.validate(email) is False
    user.refresh_from_db()
    assert user.is_pending and user.is_active
    assert user.role == role and user.password == before
    record = user.validation_records.get()
    assert record.attempted_email == email
    assert record.simulation_result == "RECUSADO"


def test_active_account_does_not_repeat_validation(academic_user_factory):
    user = academic_user_factory(email="lucas.aluno@univille.br")
    assert AcademicValidationService.validate(user.email) is True
    assert AcademicValidationService.validate(user.email) is True
    assert user.validation_records.count() == 1


def test_activation_rolls_back_if_audit_fails(academic_user_factory, monkeypatch):
    user = academic_user_factory(email="lucas.aluno@univille.br")

    def fail_audit(*args, **kwargs):
        raise RuntimeError("Falha sintética na auditoria")

    monkeypatch.setattr(AcademicValidationRecord.objects, "create", fail_audit)
    with pytest.raises(RuntimeError, match="Falha sintética"):
        AcademicValidationService.validate(user.email)
    user.refresh_from_db()
    assert user.is_pending
    assert not user.validation_records.exists()


@pytest.mark.parametrize("method", ["get", "post"])
def test_activation_requires_session(client, method):
    response = getattr(client, method)(reverse("accounts:activation"))
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/accounts/activation/"
    assert not AcademicValidationRecord.objects.exists()


def test_activation_get_shows_own_data_without_side_effects(pending_client, pending_user):
    response = pending_client.get(reverse("accounts:activation"))
    assert response.status_code == 200
    html = response.content.decode()
    assert pending_user.full_name in html and pending_user.email in html
    assert "Validar Vínculo Institucional" in html
    assert html.count('type="submit"') == 1
    assert 'name="email"' not in html and 'name="matricula"' not in html
    assert 'name="csrfmiddlewaretoken"' in html
    pending_user.refresh_from_db()
    assert pending_user.is_pending
    assert not pending_user.validation_records.exists()


@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
@pytest.mark.parametrize("email,eligible", [("lucas.aluno@univille.br", True),
                                           ("bloqueado@univille.br", False),
                                           ("ausente.sintetico@univille.br", False)])
def test_activation_post_uses_session_identity(client, academic_user_factory, role, email, eligible):
    user = academic_user_factory(email=email, role=role)
    other = academic_user_factory(email="joao.silva@univille.br")
    client.force_login(user)
    response = client.post(reverse("accounts:activation"), {"email": other.email, "user_id": other.pk})
    user.refresh_from_db()
    other.refresh_from_db()
    assert user.is_activated is eligible
    assert user.role == role
    assert other.is_pending and not other.validation_records.exists()
    record = user.validation_records.get()
    assert record.attempted_email == user.email
    assert record.simulation_result == ("APROVADO" if eligible else "RECUSADO")
    message = [str(item) for item in get_messages(response.wsgi_request)]
    if eligible:
        assert response.status_code == 302 and response.url == "/accounts/profile/"
        assert message == ["Vínculo institucional com a Univille homologado com sucesso! Sua conta está ativa."]
    else:
        assert response.status_code == 200
        assert "Não foi possível comprovar o vínculo institucional" in message[0]
        assert message[0] in response.content.decode()


@pytest.mark.parametrize("method", ["get", "post"])
def test_activation_already_active(active_client, active_user, method):
    response = getattr(active_client, method)(reverse("accounts:activation"))
    assert response.status_code == 302 and response.url == "/accounts/profile/"
    assert [str(item) for item in get_messages(response.wsgi_request)] == ["Sua conta já está ativada."]
    assert not active_user.validation_records.exists()


def test_activation_csrf(academic_user_factory):
    user = academic_user_factory(email="lucas.aluno@univille.br")
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    url = reverse("accounts:activation")
    assert client.post(url).status_code == 403
    user.refresh_from_db()
    assert user.is_pending and not user.validation_records.exists()
    assert client.get(url).status_code == 200
    response = client.post(url, {"csrfmiddlewaretoken": client.cookies["csrftoken"].value})
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.is_activated


def test_invalid_catalog_does_not_activate(academic_user_factory, settings, tmp_path):
    user = academic_user_factory(email="lucas.aluno@univille.br")
    catalog = tmp_path / "accounts" / "fixtures" / "academic_whitelist.json"
    catalog.parent.mkdir(parents=True)
    catalog.write_text("invalid-json", encoding="utf-8")
    settings.BASE_DIR = tmp_path
    with pytest.raises(json.JSONDecodeError):
        AcademicValidationService.validate(user.email)
    user.refresh_from_db()
    assert user.is_pending
    assert not user.validation_records.exists()
