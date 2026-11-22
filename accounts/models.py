"""Identidade acadêmica — Feature 001 / T002 / REQ-001, REQ-002, REQ-003."""

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, router


def validate_full_name(value):
    terms = value.split()
    if len(terms) < 2 or not all(term.isalpha() for term in terms):
        raise ValidationError("Informe nome e sobrenome, usando apenas letras.")


def validate_institutional_email(value):
    if value.rsplit("@", 1)[-1].lower() != "univille.br":
        raise ValidationError("Use um e-mail institucional @univille.br.")


class AcademicUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuários exigem is_staff=True e is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class AcademicUser(AbstractUser):
    class Role(models.TextChoices):
        MOTORISTA = "MOTORISTA", "Motorista"
        PASSAGEIRO = "PASSAGEIRO", "Passageiro"

    class AcademicStatus(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        ATIVA = "ATIVA", "Ativa"

    username = None
    first_name = None
    last_name = None
    full_name = models.CharField(max_length=150, validators=[validate_full_name])
    email = models.EmailField(unique=True, validators=[validate_institutional_email])
    role = models.CharField(max_length=20, choices=Role.choices)
    academic_status = models.CharField(
        max_length=20, choices=AcademicStatus.choices, default=AcademicStatus.PENDENTE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "role"]
    objects = AcademicUserManager()

    @property
    def display_name(self):
        terms = self.full_name.split()
        return f"{terms[0]} {terms[1][0]}." if len(terms) >= 2 else ""

    @property
    def is_pending(self):
        return self.academic_status == self.AcademicStatus.PENDENTE

    @property
    def is_activated(self):
        return self.academic_status == self.AcademicStatus.ATIVA

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name.split() else ""

    def save(self, *args, **kwargs):
        using = kwargs.get("using") or router.db_for_write(type(self), instance=self)
        original_role = None
        if self.pk is not None:
            original_role = type(self).objects.using(using).filter(pk=self.pk).values_list(
                "role", flat=True,
            ).first()
        if original_role is not None and self.role != original_role:
            raise ValidationError({"role": "O papel é imutável no MVP."})
        if original_role is None and self.academic_status != self.AcademicStatus.PENDENTE:
            raise ValidationError({"academic_status": "Toda nova conta deve iniciar PENDENTE."})
        if not self.password:
            self.set_unusable_password()
        self.full_clean()
        return super().save(*args, **kwargs)


class AcademicValidationRecord(models.Model):
    """Auditoria da validação simulada — Feature 001 / T003 / REQ-002."""

    class SimulationResult(models.TextChoices):
        APROVADO = "APROVADO", "Aprovado"
        RECUSADO = "RECUSADO", "Recusado"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="validation_records",
    )
    attempted_email = models.EmailField(max_length=254)
    simulation_result = models.CharField(max_length=20, choices=SimulationResult.choices)
    details = models.TextField(blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)
