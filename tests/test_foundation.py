"""Feature 001 / T003 — infraestrutura de REQ-002 e REQ-003."""

import pytest
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import connection
from django.template import engines
from django.template.loader import render_to_string
from django.utils import timezone


@pytest.mark.django_db
@pytest.mark.parametrize("result", ["APROVADO", "RECUSADO"])
def test_validation_audit_persists_without_activating_user(pending_user, result):
    model = apps.get_model("accounts", "AcademicValidationRecord")
    before = timezone.now()
    record = model.objects.create(
        user=pending_user, attempted_email=pending_user.email,
        simulation_result=result,
    )
    record.refresh_from_db()
    assert pending_user.validation_records.get() == record
    assert record.attempted_email == pending_user.email
    assert record.simulation_result == result
    assert record.details == ""
    assert before <= record.processed_at <= timezone.now()
    pending_user.refresh_from_db()
    assert pending_user.is_pending
    assert connection.vendor == "postgresql"


@pytest.mark.django_db
def test_audit_cascades_on_user_deletion(pending_user):
    model = apps.get_model("accounts", "AcademicValidationRecord")
    record = model.objects.create(
        user=pending_user, attempted_email=pending_user.email,
        simulation_result="RECUSADO", details="Dados de teste: vínculo não comprovado.",
    )
    pending_user.delete()
    assert not model.objects.filter(pk=record.pk).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("field,value", [
    ("attempted_email", "email-invalido"),
    ("simulation_result", "INVALIDO"),
    ("user", None),
])
def test_audit_field_validation(pending_user, field, value):
    model = apps.get_model("accounts", "AcademicValidationRecord")
    record = model(user=pending_user, attempted_email=pending_user.email,
                   simulation_result="APROVADO")
    setattr(record, field, value)
    with pytest.raises(ValidationError) as error:
        record.full_clean()
    assert field in error.value.message_dict


def test_whitelist_catalog(academic_whitelist):
    entries = {entry["email"]: entry for entry in academic_whitelist}
    assert len(entries) == len(academic_whitelist) == 4
    for entry in academic_whitelist:
        assert set(entry) == {"email", "full_name", "institutional_role", "is_eligible"}
        assert entry["email"].endswith("@univille.br")
        assert len(entry["full_name"].split()) >= 2
        assert entry["institutional_role"] in {"ALUNO", "PROFESSOR", "FUNCIONARIO"}
        assert isinstance(entry["is_eligible"], bool)
    assert entries["lucas.aluno@univille.br"]["is_eligible"] is True
    assert entries["mariana.motorista@univille.br"]["is_eligible"] is True
    assert entries["joao.silva@univille.br"]["is_eligible"] is True
    assert entries["bloqueado@univille.br"]["is_eligible"] is False
    assert "visitante.externo@univille.br" not in entries


def test_base_template_supports_inheritance_and_escapes_content():
    template = engines["django"].from_string(
        '{% extends "accounts/base.html" %}'
        '{% block title %}Página de teste{% endblock %}'
        '{% block content %}<p>{{ text }}</p>{% endblock %}'
    )
    html = template.render({"text": "<script>teste</script>"})
    assert '<html lang="pt-br">' in html
    assert "Página de teste" in html
    assert "&lt;script&gt;teste&lt;/script&gt;" in html
    assert "<script>teste</script>" not in html
    assert "Carona Univille" in render_to_string("accounts/base.html")


@pytest.mark.django_db
def test_authenticated_clients(pending_client, active_client, pending_user, active_user):
    assert pending_client.session["_auth_user_id"] == str(pending_user.pk)
    assert active_client.session["_auth_user_id"] == str(active_user.pk)
    assert pending_user.is_pending
    assert active_user.is_activated


@pytest.mark.django_db
def test_user_factory_supports_both_roles(academic_user_factory):
    driver = academic_user_factory(role="MOTORISTA")
    passenger = academic_user_factory(role="PASSAGEIRO")
    assert driver.pk != passenger.pk
    assert driver.email != passenger.email
    assert driver.role == "MOTORISTA"
    assert passenger.role == "PASSAGEIRO"
