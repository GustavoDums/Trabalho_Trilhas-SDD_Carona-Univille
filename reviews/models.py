"""Avaliações históricas, reputação e ocorrências de conduta."""
from datetime import timedelta, timezone as dt_timezone
from decimal import Context, Decimal, InvalidOperation, localcontext
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.utils import timezone

from rides.models import CancellationRecord, RideBooking, ValidatedModel, require_integer, require_aware_datetime


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


class PenaltyRecord(ValidatedModel):
    class Kind(models.TextChoices):
        CANCELAMENTO_TARDIO = 'CANCELAMENTO_TARDIO', 'Cancelamento tardio'
        NO_SHOW = 'NO_SHOW', 'Não comparecimento'

    subject = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                related_name='penalties_received')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                              null=True, blank=True, related_name='penalties_reported')
    offer = models.ForeignKey('rides.RideOffer', on_delete=models.PROTECT, related_name='penalties')
    booking = models.ForeignKey('rides.RideBooking', on_delete=models.PROTECT,
                                null=True, blank=True, related_name='penalties')
    cancellation = models.OneToOneField('rides.CancellationRecord', on_delete=models.PROTECT,
                                        null=True, blank=True, related_name='penalty')
    source_key = models.CharField(max_length=128, unique=True)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    occurred_at = models.DateTimeField(validators=[require_aware_datetime])
    reported_at = models.DateTimeField(null=True, blank=True, validators=[require_aware_datetime])
    delta = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(kind='CANCELAMENTO_TARDIO', delta=Decimal('-0.20'),
                             cancellation__isnull=False, actor__isnull=True, reported_at__isnull=True)
                    | (models.Q(kind='NO_SHOW', delta=Decimal('-0.50'), cancellation__isnull=True,
                                actor__isnull=False, booking__isnull=False, reported_at__isnull=False,
                                reported_at__gte=models.F('occurred_at'))
                       & ~models.Q(actor=models.F('subject')))
                ),
                name='penalty_kind_origin_delta_valid',
            ),
            models.UniqueConstraint(
                fields=['offer', 'subject'], condition=models.Q(kind='NO_SHOW'),
                name='penalty_one_no_show_per_offer_subject',
            ),
        ]
        indexes = [models.Index(fields=['subject', 'kind', '-occurred_at'], name='penalty_subject_kind_time')]

    @property
    def automatic_rating(self):
        return 1 if self.kind == self.Kind.NO_SHOW else None

    @staticmethod
    def apply_deductions(base_score, penalties):
        """Aplica deltas ao valor já calculado a partir das notas elegíveis."""
        deltas = {penalty.source_key: penalty.delta for penalty in penalties}
        with localcontext(Context(prec=28)):
            adjusted = sum(deltas.values(), base_score)
        return max(Decimal('0.00'), min(Decimal('5.00'), adjusted))

    def clean(self):
        super().clean()
        if self.kind == self.Kind.CANCELAMENTO_TARDIO:
            event = CancellationRecord.objects.filter(pk=self.cancellation_id).values_list(
                'actor_id', 'offer_id', 'booking_id', 'occurred_at', 'classification',
            ).first()
            expected = (self.subject_id, self.offer_id, self.booking_id, self.occurred_at,
                        CancellationRecord.Classification.TARDIO)
            if event != expected:
                raise ValidationError({'cancellation': 'Informe o evento tardio correspondente à penalidade.'})
        elif self.kind == self.Kind.NO_SHOW:
            booking = RideBooking.objects.filter(pk=self.booking_id, offer_id=self.offer_id).values_list(
                'passenger_id', 'offer__driver_id', 'status',
            ).first()
            if (booking is None or {booking[0], booking[1]} != {self.subject_id, self.actor_id}
                    or (self._state.adding and booking[2] != RideBooking.Status.CONFIRMADA)):
                raise ValidationError({'booking': 'Informe a reserva confirmada que vincula o titular à contraparte.'})


class ConductProfile(ValidatedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                related_name='conduct_profile')
    suspended_until = models.DateTimeField(null=True, blank=True, validators=[require_aware_datetime])

    def suspension_after_no_show(self, *, at):
        """Calcula o prazo na data de uma ocorrência, sem gravar a projeção."""
        require_aware_datetime(at)
        at = at.astimezone(dt_timezone.utc)
        latest = list(PenaltyRecord.objects.filter(
            subject_id=self.user_id, kind=PenaltyRecord.Kind.NO_SHOW,
            occurred_at__range=(at - timedelta(days=30), at),
        ).order_by('-occurred_at').values_list('occurred_at', flat=True)[:3])
        if len(latest) == 3 and latest[0] == at:
            return at + timedelta(days=14)
        return None

    def is_suspended_at(self, *, at):
        require_aware_datetime(at)
        if self.suspended_until is None:
            return False
        return at.astimezone(dt_timezone.utc) < self.suspended_until.astimezone(dt_timezone.utc)
