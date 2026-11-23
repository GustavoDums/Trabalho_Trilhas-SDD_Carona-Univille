"""Feature 005/T008 — remoção de ofertas do painel do motorista."""
from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.test import Client
from django.urls import reverse

from notifications.models import Notification
from rides.models import CancellationRecord, RecurringRideOccurrence, RecurringRideRule, RideBooking, RideOffer
from rides.services.cancellation_service import CancellationService

pytestmark = pytest.mark.django_db


def removal_url(offer):
    return reverse("rides:remove_offer", kwargs={"offer_id": offer.pk})


def test_open_offer_is_cancelled_and_removed_once(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    monkeypatch.setattr("django.utils.timezone.now", lambda: scene.departure - timedelta(hours=1))
    client = Client(enforce_csrf_checks=True)
    client.force_login(scene.driver)
    url = removal_url(scene.offer)
    panel = reverse("rides:my-offers")
    page = client.get(panel)
    assert f'aria-label="Remover carona {scene.offer.pk} da lista"' in page.content.decode()
    assert f'action="{url}"' in page.content.decode() and "Cancelar e remover" in page.content.decode()
    token = {"csrfmiddlewaretoken": client.cookies["csrftoken"].value}

    response = client.post(url, token, follow=True)
    assert response.redirect_chain == [(panel, 302)]
    assert list(response.context["offers"]) == []
    scene.offer.refresh_from_db()
    scene.booking.refresh_from_db()
    assert scene.offer.status == RideOffer.Status.CANCELADA
    assert scene.booking.status == RideBooking.Status.CANCELADA
    removed_at = scene.offer.removed_from_driver_at
    assert removed_at is not None
    event = CancellationRecord.objects.get(offer=scene.offer)
    assert event.classification == CancellationRecord.Classification.TARDIO
    assert Notification.objects.filter(cancellation=event, recipient=scene.passenger).count() == 1

    assert client.post(url, token).status_code == 302
    scene.offer.refresh_from_db()
    assert scene.offer.removed_from_driver_at == removed_at
    assert CancellationRecord.objects.filter(offer=scene.offer).count() == 1
    assert Notification.objects.filter(cancellation=event, recipient=scene.passenger).count() == 1


def test_cancelled_occurrence_is_removed_after_departure_preserving_history(cancellation_scene, client, monkeypatch):
    scene = cancellation_scene
    departure = scene.departure.astimezone(ZoneInfo("America/Sao_Paulo"))
    rule = RecurringRideRule.objects.create(
        driver=scene.driver, origin=scene.points[0], destination=scene.points[-1],
        weekdays=[departure.weekday()], local_time=departure.time(), seats=1,
        vehicle_model="Veículo Sintético", vehicle_color="Azul", vehicle_plate="PRIVADA",
    )
    occurrence = RecurringRideOccurrence.objects.create(rule=rule, offer=scene.offer, local_date=departure.date())
    cancelled = CancellationService.cancel_offer(
        user=scene.driver, offer_id=scene.offer.pk, clock=lambda: scene.departure - timedelta(hours=8),
    )
    events = list(CancellationRecord.objects.values())
    notices = list(Notification.objects.values())
    monkeypatch.setattr("django.utils.timezone.now", lambda: scene.departure + timedelta(days=1))
    client.force_login(scene.driver)
    page = client.get(reverse("rides:my-offers"))
    assert "Remover esta carona de Minhas ofertas?" in page.content.decode()

    response = client.post(removal_url(scene.offer), follow=True)
    assert list(response.context["offers"]) == []
    scene.offer.refresh_from_db()
    assert scene.offer.removed_from_driver_at is not None
    assert scene.offer.cancelled_at == cancelled.cancelled_at
    occurrence.refresh_from_db()
    assert occurrence.offer_id == scene.offer.pk and occurrence.rule_id == rule.pk
    assert list(CancellationRecord.objects.values()) == events
    assert list(Notification.objects.values()) == notices


def test_open_offer_at_departure_cannot_be_removed(cancellation_scene, client, monkeypatch):
    scene = cancellation_scene
    monkeypatch.setattr("django.utils.timezone.now", lambda: scene.departure)
    client.force_login(scene.driver)
    response = client.post(removal_url(scene.offer))
    assert response.status_code == 400
    assert "O cancelamento só pode ser feito antes da saída da origem." in response.content.decode()
    assert f'action="{removal_url(scene.offer)}"' not in response.content.decode()
    scene.offer.refresh_from_db()
    assert scene.offer.status == RideOffer.Status.ABERTA and scene.offer.removed_from_driver_at is None
    assert not CancellationRecord.objects.exists()


def test_removal_requires_post_csrf_and_active_owner(cancellation_scene, academic_user_factory):
    scene = cancellation_scene
    url = removal_url(scene.offer)
    client = Client(enforce_csrf_checks=True)
    assert client.post(url).status_code == 302
    client.force_login(scene.driver)
    assert client.get(url).status_code == 405
    assert client.post(url).status_code == 403
    client.get(reverse("rides:my-offers"))
    token = {"csrfmiddlewaretoken": client.cookies["csrftoken"].value}
    assert client.post(reverse("rides:remove_offer", kwargs={"offer_id": 999999}), token).status_code == 400
    other_driver = academic_user_factory(role="MOTORISTA")
    other_driver.academic_status = "ATIVA"
    other_driver.save(update_fields=["academic_status", "updated_at"])
    client.force_login(other_driver)
    client.get(reverse("rides:my-offers"))
    token = {"csrfmiddlewaretoken": client.cookies["csrftoken"].value}
    assert client.post(url, token).status_code == 403
    scene.offer.refresh_from_db()
    assert scene.offer.status == RideOffer.Status.ABERTA and scene.offer.removed_from_driver_at is None
    assert not CancellationRecord.objects.exists()


def test_removal_failure_rolls_back_cancellation_and_side_effects(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    original_save = RideOffer.save
    notices = list(Notification.objects.values())
    monkeypatch.setattr("django.utils.timezone.now", lambda: scene.departure - timedelta(hours=1))

    def reject_removal(offer, *args, **kwargs):
        if offer.removed_from_driver_at is not None:
            raise ValidationError("Falha simulada na remoção.")
        return original_save(offer, *args, **kwargs)

    monkeypatch.setattr(RideOffer, "save", reject_removal)
    with pytest.raises(ValidationError, match="Falha simulada"):
        CancellationService.remove_offer(user=scene.driver, offer_id=scene.offer.pk)
    scene.offer.refresh_from_db()
    scene.booking.refresh_from_db()
    assert scene.offer.status == RideOffer.Status.ABERTA and scene.offer.cancelled_at is None
    assert scene.offer.removed_from_driver_at is None
    assert scene.booking.status == RideBooking.Status.CONFIRMADA
    assert not CancellationRecord.objects.exists()
    assert list(Notification.objects.values()) == notices
