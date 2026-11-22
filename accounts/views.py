"""Cadastro institucional — Feature 001 / T005 / REQ-001 e REQ-002."""

from django.contrib import messages
from django.views.generic.edit import CreateView

from .forms import AcademicRegistrationForm


class RegisterView(CreateView):
    form_class = AcademicRegistrationForm
    template_name = "accounts/register.html"
    # Destino aprovado; a tela de login será implementada na T010.
    success_url = "/accounts/login/"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Cadastro realizado com sucesso! Conclua a validação do seu vínculo acadêmico para ativar sua conta.",
        )
        return response
