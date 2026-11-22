"""Fixtures compartilhadas da Feature 001 / T003, apenas com dados sintéticos."""

import itertools
import json

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.fixture
def academic_whitelist():
    path = settings.BASE_DIR / "accounts" / "fixtures" / "academic_whitelist.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def academic_user_factory(db):
    sequence = itertools.count(1)

    def create_user(**overrides):
        values = {
            "email": f"usuario.sintetico{next(sequence)}@univille.br",
            "full_name": "Usuário Sintético",
            "role": "PASSAGEIRO",
            "password": "Senha-sintetica-2026!",
        }
        values.update(overrides)
        return get_user_model().objects.create_user(**values)

    return create_user


@pytest.fixture
def pending_user(academic_user_factory):
    return academic_user_factory()


@pytest.fixture
def active_user(academic_user_factory):
    user = academic_user_factory()
    user.academic_status = "ATIVA"
    user.save(update_fields=["academic_status", "updated_at"])
    return user


@pytest.fixture
def pending_client(pending_user):
    client = Client()
    client.force_login(pending_user)
    return client


@pytest.fixture
def active_client(active_user):
    client = Client()
    client.force_login(active_user)
    return client
