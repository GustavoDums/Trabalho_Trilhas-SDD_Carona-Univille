"""Feature 007/T002 unificada — média simples das últimas 20 avaliações."""
from datetime import datetime, timezone as dt_timezone
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import ReputationProfile, RideReview

WINDOW_SIZE = 20


def calculate_score(ratings):
    """Calcula apenas o conjunto já selecionado, sem base virtual ou float."""
    try:
        values = tuple(ratings)
    except TypeError:
        raise ValidationError('Informe uma sequência de notas inteiras.', code='invalid_ratings')
    if len(values) > WINDOW_SIZE:
        raise ValidationError('O conjunto selecionado deve conter no máximo 20 avaliações.', code='invalid_window')
    if any(isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5 for value in values):
        raise ValidationError('As notas devem ser inteiras entre 1 e 5.', code='invalid_rating')
    if not values:
        return Decimal('5.00')
    with localcontext(Context(prec=28, rounding=ROUND_HALF_UP)):
        return (Decimal(sum(values))/Decimal(len(values))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class ReputationService:
    @staticmethod
    @transaction.atomic
    def rebuild(*, user_id, at=None):
        if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError({'user_id': 'Selecione um usuário válido.'})
        user = get_user_model().objects.select_for_update().filter(pk=user_id).first()
        if user is None:
            raise ValidationError({'user_id': 'Selecione um usuário existente.'})
        instant = timezone.now() if at is None else at
        if not isinstance(instant, datetime) or timezone.is_naive(instant):
            raise ValidationError('Informe um instante com fuso definido.', code='invalid_time')
        instant = instant.astimezone(dt_timezone.utc)
        ratings = list(RideReview.objects.filter(
            reviewed_user_id=user.pk, created_at__lte=instant,
        ).order_by('-created_at', '-id').values_list('rating', flat=True)[:WINDOW_SIZE])
        score = calculate_score(ratings)
        profile = ReputationProfile.objects.select_for_update().filter(user_id=user.pk).first()
        if profile is None:
            profile = ReputationProfile(user=user)
        profile.score = score
        profile.computed_at = instant
        profile.save()
        return profile
