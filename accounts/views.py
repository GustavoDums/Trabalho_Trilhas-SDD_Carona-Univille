"""Cadastro institucional — Feature 001 / T005 / REQ-001 e REQ-002."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.shortcuts import redirect

from reviews.models import ConductProfile, PenaltyRecord, ReputationProfile
from reviews.services.reputation_service import INITIAL_SCORE

from .forms import AcademicAuthenticationForm, AcademicRegistrationForm
from .services import AcademicValidationService


class RegisterView(CreateView):
    duplicate_message = (
        "Não foi possível concluir o cadastro com os dados informados. "
        "Se você já possui vínculo cadastrado, tente fazer login."
    )
    form_class = AcademicRegistrationForm
    template_name = "accounts/register.html"
    # Cadastro aprovado com login manual.
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


class LoginView(DjangoLoginView):
    """T010: login manual, com destino definido pelo vínculo acadêmico."""

    template_name = "accounts/login.html"
    authentication_form = AcademicAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return "/accounts/activation/" if self.request.user.is_pending else "/accounts/profile/"


class ProfileView(LoginRequiredMixin, TemplateView):
    """T010: perfil próprio; o middleware restringe contas pendentes."""

    template_name = "accounts/profile.html"
    login_url = "/accounts/login/"
    http_method_names = ["get", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        score = ReputationProfile.objects.filter(user_id=self.request.user.pk).values_list("score", flat=True).first()
        context["reputation_score"] = INITIAL_SCORE if score is None else score
        return context


@method_decorator(never_cache, name="dispatch")
class PenaltiesHistoryView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/penalties_history.html"
    login_url = "/accounts/login/"
    http_method_names = ["get", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.pk
        profile = ConductProfile.objects.filter(user_id=user_id).only("suspended_until").first()
        context["suspended_until"] = profile.suspended_until if profile else None
        context["suspension_active"] = profile is not None and profile.is_suspended_at(at=timezone.now())
        context["penalties"] = PenaltyRecord.objects.filter(subject_id=user_id).only(
            "kind", "occurred_at", "delta",
        ).order_by("-occurred_at", "-pk")
        return context
