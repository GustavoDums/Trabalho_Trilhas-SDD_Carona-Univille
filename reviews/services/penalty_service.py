"""Materialização transacional de penalidades a partir do evento de origem."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from rides.models import CancellationRecord, RideBooking, RideOffer
from ..models import ConductProfile, PenaltyRecord
from .reputation_service import ReputationService
from .review_service import _accounts, _authenticated, _eligible, _instant, _offer, _valid_id


def _report_inputs(*, user, booking_id, clock):
    _authenticated(user)
    _valid_id(booking_id, 'booking_id')
    reference = RideBooking.objects.filter(pk=booking_id).values('offer_id', 'passenger_id').first()
    if reference is None:
        raise PermissionDenied('A denúncia exige uma contraparte confirmada.')
    offer = _offer(reference['offer_id'])
    accounts = _accounts(offer.driver_id, reference['passenger_id'])
    actor = accounts.get(user.pk)
    driver = accounts[offer.driver_id]
    passenger = accounts[reference['passenger_id']]
    if not _eligible(actor) or driver.role != 'MOTORISTA' or passenger.role != 'PASSAGEIRO':
        raise PermissionDenied('A denúncia exige uma contraparte confirmada com vínculo ativo.')

    booking = RideBooking.objects.select_for_update(no_key=True).filter(
        pk=booking_id, offer=offer, passenger=passenger, status=RideBooking.Status.CONFIRMADA,
    ).first()
    if booking is None or offer.status == RideOffer.Status.CANCELADA:
        raise ValidationError('A reserva precisa estar confirmada em uma oferta não cancelada.')

    driver_reporting = user.pk == driver.pk
    if ((not driver_reporting and booking.no_show_at is not None) or
            PenaltyRecord.objects.filter(offer=offer, subject_id=user.pk, kind=PenaltyRecord.Kind.NO_SHOW).exists()):
        raise PermissionDenied('A denúncia exige participação na carona.')
    if booking.boarding_point_id != offer.origin_id:
        raise ValidationError('A denúncia exige um horário previsto para o ponto de embarque.')
    occurred_at = offer.departure_at + timedelta(minutes=10)
    reference_at = offer.completed_at
    if reference_at is None:
        if driver_reporting:
            raise ValidationError('Registre a conclusão da carona antes da denúncia.')
        reference_at = occurred_at
    reported_at = _instant(clock)
    if not max(occurred_at, reference_at) <= reported_at <= reference_at + timedelta(hours=2):
        raise ValidationError('A denúncia está fora da janela permitida.')
    subject = passenger if driver_reporting else driver
    return booking, actor, subject, occurred_at, reported_at


def _update_suspension(penalty):
    profile = ConductProfile.objects.select_for_update().filter(user_id=penalty.subject_id).first()
    if profile is None:
        profile = ConductProfile(user_id=penalty.subject_id)
    # Uma denúncia fora de ordem pode completar a janela de uma ocorrência posterior.
    last_candidate = min(penalty.reported_at, penalty.occurred_at + timedelta(days=30))
    candidates = PenaltyRecord.objects.filter(
        subject_id=penalty.subject_id, kind=PenaltyRecord.Kind.NO_SHOW,
        occurred_at__range=(penalty.occurred_at, last_candidate),
    ).order_by('-occurred_at').values_list('occurred_at', flat=True).distinct()
    for occurred_at in candidates:
        until = profile.suspension_after_no_show(at=occurred_at)
        if until is not None:
            if profile.suspended_until is None or until > profile.suspended_until:
                profile.suspended_until = until
                profile.save()
            break


class PenaltyService:
    @staticmethod
    @transaction.atomic
    def no_show_context(*, user, booking_id, clock=None):
        booking, _, subject, _, _ = _report_inputs(user=user, booking_id=booking_id, clock=clock)
        return {'booking_id': booking.pk, 'counterpart_name': subject.display_name}

    @staticmethod
    @transaction.atomic
    def report_no_show(*, user, booking_id, declared, clock=None):
        booking, actor, subject, occurred_at, reported_at = _report_inputs(
            user=user, booking_id=booking_id, clock=clock,
        )
        if declared is not True:
            raise ValidationError('Confirme a declaração de ausência para enviar a denúncia.')
        penalty, created = PenaltyRecord.objects.get_or_create(
            offer_id=booking.offer_id, subject=subject, kind=PenaltyRecord.Kind.NO_SHOW,
            defaults={
                'actor': actor,
                'booking': booking,
                'source_key': f'no-show:{booking.offer_id}:{subject.pk}',
                'occurred_at': occurred_at,
                'reported_at': reported_at,
                'delta': Decimal('-0.50'),
            },
        )
        if created:
            if subject.pk == booking.passenger_id and booking.no_show_at is None:
                booking.no_show_at = occurred_at
                booking.save(update_fields=['no_show_at', 'updated_at'])
            _update_suspension(penalty)
            ReputationService.rebuild(user_id=subject.pk, at=reported_at)
        return penalty

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
