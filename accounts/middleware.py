"""Confinamento acadêmico — Feature 001 / T009 / REQ-002 e REQ-003."""

from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.cache import add_never_cache_headers

from reviews.services.conduct_service import active_suspension_until


class AcademicStatusMiddleware:
    public_paths = {"/accounts/login/", "/accounts/register/"}
    pending_paths = {"/accounts/activation/", "/accounts/logout/"}
    suspension_actions = {
        "rides:offer-create": {"GET", "HEAD", "POST"},
        "rides:book": {"POST"},
        "rides:recurring_offers": {"POST"},
    }

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

    def process_view(self, request, view_func, view_args, view_kwargs):
        methods = self.suspension_actions.get(request.resolver_match.view_name, ())
        if request.method not in methods:
            return None
        until = active_suspension_until(request.user.pk, at=timezone.now())
        if until is None:
            return None
        response = render(request, "accounts/suspended_action.html", {"suspended_until": until}, status=403)
        add_never_cache_headers(response)
        return response
