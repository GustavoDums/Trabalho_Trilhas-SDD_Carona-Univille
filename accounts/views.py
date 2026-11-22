"""Cadastro institucional — Feature 001 / T005 / REQ-001 e REQ-002."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.shortcuts import redirect

from .forms import AcademicRegistrationForm
from .services import AcademicValidationService


class RegisterView(CreateView):
    duplicate_message = (
        "Não foi possível concluir o cadastro com os dados informados. "
        "Se você já possui vínculo cadastrado, tente fazer login."
    )
    form_class = AcademicRegistrationForm
    template_name = "accounts/register.html"
    # Destino aprovado; a tela de login será implementada na T010.
    success_url = "/accounts/login/"

    def form_valid(self, form):
        try:
            # O savepoint permite renderizar o erro após rejeição pela UNIQUE.
            with transaction.atomic():
                response = super().form_valid(form)
        except ValidationError as error:
            if not any(item.code == "unique" for item in getattr(error, "error_dict", {}).get("email", [])):
                raise
            return self.duplicate_response(form)
        except IntegrityError as error:
            cause = error.__cause__
            if getattr(cause, "sqlstate", None) != "23505":
                raise
            with connection.cursor() as cursor:
                constraints = connection.introspection.get_constraints(cursor, form._meta.model._meta.db_table)
            constraint = constraints.get(cause.diag.constraint_name, {})
            if not constraint.get("unique") or constraint.get("columns") != ["email"]:
                raise
            return self.duplicate_response(form)
        messages.success(
            self.request,
            "Cadastro realizado com sucesso! Conclua a validação do seu vínculo acadêmico para ativar sua conta.",
        )
        return response

    def duplicate_response(self, form):
        form.add_error(None, self.duplicate_message)
        return super().form_invalid(form)


    def form_invalid(self, form):
        email_errors = form.errors.as_data().get("email", [])
        if any(error.code == "unique" for error in email_errors):
            # Substitui a mensagem de unicidade sem esconder outras validações.
            remaining = [error for error in email_errors if error.code != "unique"]
            del form.errors["email"]
            for error in remaining:
                form.add_error("email", error)
            return self.duplicate_response(form)
        return super().form_invalid(form)


class ActivationView(LoginRequiredMixin, TemplateView):
    """T008 / REQ-002: a identidade vem exclusivamente da sessão."""

    template_name = "accounts/activation.html"
    login_url = "/accounts/login/"
    http_method_names = ["get", "post", "head", "options"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_activated:
            messages.info(request, "Sua conta já está ativada.")
            return redirect("/accounts/profile/")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if AcademicValidationService.validate(request.user.email):
            messages.success(
                request,
                "Vínculo institucional com a Univille homologado com sucesso! Sua conta está ativa.",
            )
            return redirect("/accounts/profile/")
        messages.error(
            request,
            "Não foi possível comprovar o vínculo institucional para este e-mail na base acadêmica simulada. "
            "Verifique se seu cadastro consta na lista de homologação da PoC.",
        )
        return self.render_to_response(self.get_context_data())
