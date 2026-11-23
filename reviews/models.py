"""Feature 006/T002 — histórico de avaliação; elegibilidade no serviço."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
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
