"""Feature 002/T003 — fronteira transacional de publicação."""

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import RideOffer, RoutePoint, Waypoint


@transaction.atomic
def publish_offer(*, driver, data, points):
    author = get_user_model().objects.select_for_update().get(pk=driver.pk)
    if not (author.is_active and author.role == "MOTORISTA" and author.is_activated):
        raise PermissionDenied("Somente motoristas com vínculo ativo podem publicar.")
    fields = ("origin", "destination", "departure_at", "seats", "vehicle_model", "vehicle_color", "vehicle_plate")
    values = {field: data[field] for field in fields}
    offer = RideOffer(driver=author, **values)
    offer.full_clean()
    itinerary = [offer.origin_id, *[point.pk for point in points], offer.destination_id]
    if len(itinerary) != len(set(itinerary)):
        raise ValidationError("Origem, paradas e destino devem ser pontos distintos.")
    if RoutePoint.objects.filter(pk__in=itinerary).count() != len(itinerary):
        raise ValidationError("Selecione somente pontos do catálogo.")
    offer.save()
    for position, point in enumerate(points, start=1):
        Waypoint.objects.create(offer=offer, point=point, position=position)
    return offer
