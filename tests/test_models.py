"""Feature 001 / T002 — REQ-001, REQ-002, REQ-003."""

import pytest
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction


pytestmark = pytest.mark.django_db


def account(**overrides):
    values = dict(email="conta.sintetica@univille.br", full_name="Pessoa Sintética",
                  role="PASSAGEIRO")
    values.update(overrides)
    return get_user_model()(**values)


def test_custom_identity():
    model = get_user_model()
    assert issubclass(model, AbstractUser)
    assert model._meta.label == "accounts.AcademicUser"
    assert model.USERNAME_FIELD == "email"
    assert connection.vendor == "postgresql"


@pytest.mark.parametrize("role", ["MOTORISTA", "PASSAGEIRO"])
def test_new_account_is_pending(role):
    user = account(role=role)
    user.save()
    user.refresh_from_db()
    assert user.role == role
    assert user.academic_status == "PENDENTE"
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_pending and not user.is_activated
    assert user.created_at and user.updated_at


def test_initial_active_status_is_rejected():
    with pytest.raises(ValidationError, match="PENDENTE"):
        account(academic_status="ATIVA").save()


def test_email_unique_in_database():
    user = account()
    user.save()
    with pytest.raises(IntegrityError), transaction.atomic():
        get_user_model().objects.bulk_create([account()])
    assert get_user_model().objects.filter(email=user.email).count() == 1


@pytest.mark.parametrize("name", ["", "   ", "Pessoa", " Pessoa  ", "Pessoa 123", "Pessoa @Teste"])
def test_invalid_full_name(name):
    with pytest.raises(ValidationError) as error:
        account(full_name=name).save()
    assert "full_name" in error.value.message_dict


@pytest.mark.parametrize("name", ["Pessoa Sintética", "  João   da Silva  "])
def test_valid_full_name(name):
    user = account(full_name=name)
    user.save()
    assert user.display_name == ("Pessoa S." if name.startswith("Pessoa") else "João d.")


@pytest.mark.parametrize("field,value", [("role", ""), ("role", "HIBRIDO"),
                                        ("academic_status", "INVALIDO")])
def test_invalid_choices(field, value):
    with pytest.raises(ValidationError) as error:
        account(**{field: value}).save()
    assert field in error.value.message_dict


@pytest.mark.parametrize("role,new_role", [("MOTORISTA", "PASSAGEIRO"),
                                         ("PASSAGEIRO", "MOTORISTA")])
def test_role_is_immutable(role, new_role):
    user = account(role=role)
    user.save()
    user.role = new_role
    with pytest.raises(ValidationError) as error:
        user.save()
    assert "role" in error.value.message_dict
    user.refresh_from_db()
    assert user.role == role


def test_existing_account_can_be_activated():
    user = account()
    user.save()
    user.academic_status = "ATIVA"
    user.save(update_fields=["academic_status", "updated_at"])
    user.refresh_from_db()
    assert user.is_activated and not user.is_pending
    user.full_name = "Pessoa Atualizada"
    user.save()
    user.refresh_from_db()
    assert user.full_name == "Pessoa Atualizada"


@pytest.mark.parametrize("email", ["@univille.br", "nome..invalido@univille.br", "pessoa@example.org"])
def test_invalid_institutional_email(email):
    with pytest.raises(ValidationError) as error:
        account(email=email).save()
    assert "email" in error.value.message_dict


def test_manager_and_email_authentication():
    user = get_user_model().objects.create_user(
        email="login.sintetico@univille.br", full_name="Login Sintético",
        role="PASSAGEIRO", password="Senha-sintetica-2026!",
    )
    assert user.check_password("Senha-sintetica-2026!")
    assert authenticate(email=user.email, password="Senha-sintetica-2026!") == user


def test_superuser_manager():
    user = get_user_model().objects.create_superuser(
        email="admin.sintetico@univille.br", full_name="Admin Sintético",
        role="MOTORISTA", password="Senha-sintetica-2026!",
    )
    assert user.is_staff and user.is_superuser
    assert user.academic_status == "PENDENTE"
