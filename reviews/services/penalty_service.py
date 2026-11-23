"""Materialização transacional de penalidades a partir do evento de origem."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from rides.models import CancellationRecord, RideOffer
from ..models import PenaltyRecord
from .reputation_service import ReputationService


class PenaltyService:
    @staticmethod
    @transaction.atomic
    def apply_cancellation(*, cancellation_id):
        event = CancellationRecord.objects.get(pk=cancellation_id)
        if event.classification != CancellationRecord.Classification.TARDIO:
            return None

        # Segue a ordem de locks do cancelamento, inclusive no reprocessamento isolado.
        RideOffer.objects.select_for_update(no_key=True).only('pk').get(pk=event.offer_id)
        get_user_model().objects.select_for_update(no_key=True).only('pk').get(pk=event.actor_id)
        penalty, _ = PenaltyRecord.objects.get_or_create(cancellation=event, defaults={
            'subject_id': event.actor_id,
            'offer_id': event.offer_id,
            'booking_id': event.booking_id,
            'source_key': f'cancellation:{event.pk}',
            'kind': PenaltyRecord.Kind.CANCELAMENTO_TARDIO,
            'occurred_at': event.occurred_at,
            'delta': Decimal('-0.20'),
        })
        # O reprocessamento recompõe o cache atual, inclusive se ele tiver sido removido.
        reference = max(timezone.now(), event.occurred_at)
        ReputationService.rebuild(user_id=event.actor_id, at=reference)
        return penalty
