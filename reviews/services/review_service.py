"""Feature 006/T002 — conclusão explícita e avaliação em janela UTC fechada."""
from datetime import datetime, timedelta, timezone as dt_timezone

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from rides.models import RideBooking, RideOffer
from ..models import RideReview


def _authenticated(user):
    if not getattr(user, 'is_authenticated', False) or getattr(user, 'pk', None) is None:
        raise PermissionDenied('É necessário vínculo acadêmico ativo.')


def _valid_id(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValidationError({field: 'Selecione um identificador válido.'})


def _offer(offer_id):
    _valid_id(offer_id, 'offer_id')
    offer = RideOffer.objects.select_for_update().filter(pk=offer_id).first()
    if offer is None:
        raise ValidationError({'offer_id': 'Selecione uma oferta existente.'})
    return offer


def _accounts(*ids):
    return {user.pk: user for user in get_user_model().objects.select_for_update().filter(
        pk__in=ids).order_by('pk')}


def _eligible(user):
    return user is not None and user.is_active and user.is_activated


def _instant(clock):
    now = (clock or timezone.now)()
    if not isinstance(now, datetime) or timezone.is_naive(now):
        raise ValidationError('Informe um instante com fuso definido.', code='invalid_time')
    return now.astimezone(dt_timezone.utc)


class ReviewService:
    @staticmethod
    @transaction.atomic
    def complete_offer(*, user, offer_id, clock=None):
        _authenticated(user)
        offer = _offer(offer_id)
        accounts = _accounts(user.pk, offer.driver_id)
        actor = accounts.get(user.pk)
        if not _eligible(actor) or actor.pk != offer.driver_id or actor.role != 'MOTORISTA':
            raise PermissionDenied('Somente o motorista titular ativo pode concluir a oferta.')
        if offer.status == RideOffer.Status.CANCELADA:
            raise ValidationError('Oferta cancelada não pode ser concluída.', code='cancelled_offer')
        if offer.completed_at is not None:
            return offer
        now = _instant(clock)
        if now < offer.departure_at:
            raise ValidationError('A conclusão não pode ocorrer antes da partida.', code='before_departure')
        offer.completed_at = now
        offer.save(update_fields=['completed_at'])
        return offer

    @staticmethod
    @transaction.atomic
    def create_review(*, user, offer_id, reviewed_user_id, rating, comment='', clock=None):
        _authenticated(user)
        _valid_id(reviewed_user_id, 'reviewed_user_id')
        offer = _offer(offer_id)
        accounts = _accounts(user.pk, reviewed_user_id, offer.driver_id)
        actor, target = accounts.get(user.pk), accounts.get(reviewed_user_id)
        if target is None:
            raise ValidationError({'reviewed_user_id': 'Selecione uma contraparte existente.'})
        if not _eligible(actor) or not _eligible(target):
            raise PermissionDenied('Somente participantes com vínculo ativo podem avaliar.')
        if actor.pk == offer.driver_id and actor.role == 'MOTORISTA' and target.role == 'PASSAGEIRO':
            passenger_id = target.pk
        elif target.pk == offer.driver_id and target.role == 'MOTORISTA' and actor.role == 'PASSAGEIRO':
            passenger_id = actor.pk
        else:
            raise PermissionDenied('A avaliação exige motorista e passageiro da mesma oferta.')
        booking = RideBooking.objects.select_for_update().filter(
            offer=offer, passenger_id=passenger_id, status=RideBooking.Status.CONFIRMADA,
        ).order_by('pk').first()
        if booking is None or booking.no_show_at is not None:
            raise ValidationError('Participação não elegível para avaliação.', code='ineligible_booking')
        if offer.status == RideOffer.Status.CANCELADA or offer.completed_at is None:
            raise ValidationError('A oferta precisa estar concluída e não cancelada.', code='not_completed')
        now = _instant(clock)
        if not offer.completed_at <= now <= offer.completed_at+timedelta(hours=48):
            raise ValidationError('Avaliação fora da janela de 48 horas.', code='outside_review_window')
        result = RideReview(offer=offer, reviewer=actor, reviewed_user=target,
                            rating=rating, comment=comment, created_at=now)
        result.save()
        return result
