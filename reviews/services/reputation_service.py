"""Reputação reconstruída a partir das avaliações e penalidades registradas."""
from datetime import datetime, timezone as dt_timezone
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext
from heapq import merge
from itertools import islice

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import PenaltyRecord, ReputationProfile, RideReview

WINDOW_SIZE = 20
INITIAL_SCORE = Decimal('5.00')


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
        return INITIAL_SCORE
    with localcontext(Context(prec=28, rounding=ROUND_HALF_UP)):
        return (Decimal(sum(values))/Decimal(len(values))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _score_at(user_id, instant):
    reviews = RideReview.objects.filter(reviewed_user_id=user_id, created_at__lte=instant).order_by(
        '-created_at', '-pk',
    ).values_list('created_at', 'pk', 'rating')[:WINDOW_SIZE]
    penalties = list(PenaltyRecord.objects.filter(subject_id=user_id, occurred_at__lte=instant)
                     .only('kind', 'source_key', 'occurred_at', 'delta').order_by('-occurred_at', '-pk'))

    # Em empate entre origens, avaliações mútuas vêm primeiro e cada origem usa seu próprio PK.
    peer_ratings = ((created_at, 1, pk, rating) for created_at, pk, rating in reviews)
    automatic_ratings = ((record.occurred_at, 0, record.pk, record.automatic_rating)
                         for record in penalties if record.kind == PenaltyRecord.Kind.NO_SHOW)
    window = islice(merge(peer_ratings, automatic_ratings, reverse=True), WINDOW_SIZE)
    base_score = calculate_score(rating for _, _, _, rating in window)
    return PenaltyRecord.apply_deductions(base_score, penalties)


class ReputationService:
    @staticmethod
    @transaction.atomic
    def rebuild(*, user_id, at=None):
        if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError({'user_id': 'Selecione um usuário válido.'})
        # Serializa recálculos sem bloquear a verificação das FKs de avaliações concorrentes.
        user = get_user_model().objects.select_for_update(no_key=True).filter(pk=user_id).first()
        if user is None:
            raise ValidationError({'user_id': 'Selecione um usuário existente.'})
        instant = timezone.now() if at is None else at
        if not isinstance(instant, datetime) or timezone.is_naive(instant):
            raise ValidationError('Informe um instante com fuso definido.', code='invalid_time')
        instant = instant.astimezone(dt_timezone.utc)
        score = _score_at(user.pk, instant)
        profile = ReputationProfile.objects.select_for_update().filter(user_id=user.pk).first()
        if profile is None:
            profile = ReputationProfile(user=user)
        profile.score = score
        profile.computed_at = instant
        profile.save()
        return profile
