"""Confinamento acadêmico — Feature 001 / T009 / REQ-002 e REQ-003."""

from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


class AcademicStatusMiddleware:
    public_paths = {"/accounts/login/", "/accounts/register/"}
    pending_paths = {"/accounts/activation/", "/accounts/logout/"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        static_path = "/" + urlsplit(settings.STATIC_URL).path.strip("/") + "/"
        if request.path_info.startswith(static_path):
            return self.get_response(request)

        if not request.user.is_authenticated:
            if request.path_info in self.public_paths:
                return self.get_response(request)
            return redirect_to_login(request.get_full_path(), login_url="/accounts/login/")

        if request.user.is_pending and request.path_info not in self.pending_paths:
            messages.info(request, "Valide seu vínculo acadêmico para acessar a plataforma.")
            return redirect("/accounts/activation/")

        return self.get_response(request)
