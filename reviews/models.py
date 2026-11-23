"""Features 006/007 — avaliações históricas e projeção de reputação."""
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.utils import timezone

from rides.models import ValidatedModel, require_integer, require_aware_datetime


class RideReview(ValidatedModel):
    offer = models.ForeignKey('rides.RideOffer', on_delete=models.PROTECT, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reviews_written')
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reviews_received')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now, editable=False, validators=[require_aware_datetime])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['offer', 'reviewer', 'reviewed_user'], name='review_pair_unique'),
            models.CheckConstraint(condition=models.Q(rating__gte=1, rating__lte=5), name='review_rating_valid'),
            models.CheckConstraint(condition=~models.Q(reviewer=models.F('reviewed_user')), name='review_users_distinct'),
        ]

    @transaction.atomic
    def save(self, *args, **kwargs):
        # A avaliação e a projeção disparada pelo post_save são persistidas juntas.
        return super().save(*args, **kwargs)

    def clean_fields(self, exclude=None):
        if 'rating' not in (exclude or []):
            require_integer(self.rating, 'rating')
        if isinstance(self.comment, str):
            self.comment = self.comment.strip()
        elif 'comment' not in (exclude or []):
            raise ValidationError({'comment': 'Informe texto ou deixe o comentário vazio.'})
        super().clean_fields(exclude=exclude)

    def clean(self):
        super().clean()
        fields = ('offer_id', 'reviewer_id', 'reviewed_user_id', 'rating', 'comment', 'created_at')
        if not self._state.adding:
            previous = type(self).objects.filter(pk=self.pk).values(*fields).first()
            if previous is not None and any(getattr(self, field) != previous[field] for field in fields):
                raise ValidationError('Avaliações publicadas não podem ser editadas.', code='immutable_review')


class ReputationProfile(ValidatedModel):
    """Projeção reconstruível das avaliações recebidas."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                               related_name='reputation_profile')
    score = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('5.00'),
                                validators=[MinValueValidator(Decimal('0.00')),
                                            MaxValueValidator(Decimal('5.00'))])
    computed_at = models.DateTimeField(null=True, blank=True, validators=[require_aware_datetime])

    class Meta:
        constraints = [models.CheckConstraint(
            condition=models.Q(score__gte=Decimal('0.00'), score__lte=Decimal('5.00')),
            name='reputation_score_range',
        )]

    def clean_fields(self, exclude=None):
        if 'score' not in (exclude or []):
            try:
                if isinstance(self.score, (float, bool)):
                    raise ValueError
                value = Decimal(self.score)
                if not value.is_finite():
                    raise ValueError
            except (InvalidOperation, TypeError, ValueError):
                raise ValidationError({'score': 'Informe uma pontuação Decimal finita e exata.'})
            self.score = value
        super().clean_fields(exclude=exclude)
