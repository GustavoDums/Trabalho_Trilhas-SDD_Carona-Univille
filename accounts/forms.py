"""Cadastro acadêmico — Feature 001 / T004 / REQ-001 e REQ-002."""

from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import AcademicUser


class AcademicRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha", strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password_confirm = forms.CharField(
        label="Confirme a senha", strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = AcademicUser
        fields = ("full_name", "email", "role")
        labels = {"full_name": "Nome completo", "email": "E-mail institucional", "role": "Papel"}
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }
        help_texts = {
            "full_name": "Informe pelo menos nome e sobrenome.",
            "email": "Use seu e-mail @univille.br.",
        }

    def clean_password_confirm(self):
        confirmation = self.cleaned_data["password_confirm"]
        password = self.cleaned_data.get("password")
        if password and password != confirmation:
            raise ValidationError("As senhas não conferem.", code="password_mismatch")
        return confirmation

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get("password")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            self.save_m2m()
        return user
