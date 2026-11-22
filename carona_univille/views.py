"""Placeholder de caronas — Feature 001 / T011 / REQ-002."""

from django.http import HttpResponse


def caronas(request):
    """Acesso acadêmico controlado pelo AcademicStatusMiddleware."""
    return HttpResponse(
        "Área de caronas — as funcionalidades de caronas estarão disponíveis em uma próxima etapa.",
        content_type="text/plain; charset=utf-8",
    )
