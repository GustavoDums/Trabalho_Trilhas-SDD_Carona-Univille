"""Validação institucional simulada — Feature 001 / T007 / REQ-002."""

import json

from django.conf import settings
from django.db import transaction

from .models import AcademicUser, AcademicValidationRecord


class AcademicValidationService:
    @staticmethod
    def validate(email):
        """Valida o e-mail da conta persistida, retornando sua elegibilidade.

        Falhas de leitura ou persistência são propagadas sem ativação parcial.
        A camada HTTP será responsável pela identificação do usuário na T008.
        """
        with transaction.atomic():
            user = AcademicUser.objects.select_for_update().get(email=email)
            if user.is_activated:
                return True

            path = settings.BASE_DIR / "accounts" / "fixtures" / "academic_whitelist.json"
            whitelist = json.loads(path.read_text(encoding="utf-8"))
            eligible = any(
                entry["email"] == user.email and entry["is_eligible"] is True
                for entry in whitelist
            )
            if eligible:
                user.academic_status = AcademicUser.AcademicStatus.ATIVA
                user.save(update_fields=["academic_status", "updated_at"])

            AcademicValidationRecord.objects.create(
                user=user,
                attempted_email=user.email,
                simulation_result=(
                    AcademicValidationRecord.SimulationResult.APROVADO
                    if eligible else AcademicValidationRecord.SimulationResult.RECUSADO
                ),
                details="Vínculo confirmado na base simulada." if eligible else "Vínculo não comprovado na base simulada.",
            )
            return eligible
