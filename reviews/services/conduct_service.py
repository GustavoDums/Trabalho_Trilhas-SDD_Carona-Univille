"""Consulta da suspensão disciplinar para ações protegidas."""
from django.core.exceptions import PermissionDenied

from ..models import ConductProfile


def active_suspension_until(user_id, *, at):
    return ConductProfile.objects.filter(
        user_id=user_id, suspended_until__gt=at,
    ).values_list('suspended_until', flat=True).first()


def require_unsuspended(user_id, *, at):
    if active_suspension_until(user_id, at=at) is not None:
        raise PermissionDenied('Suspensão disciplinar em vigor.')
