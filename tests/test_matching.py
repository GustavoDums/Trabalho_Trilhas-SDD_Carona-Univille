"""Feature 003/T002 local — roadmap T017; REQ-005, REQ-002, REQ-003, REQ-017."""
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone as dt_timezone
from importlib import import_module
from itertools import product
from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from rides.models import RideOffer, RoutePoint, Waypoint

NOW = datetime(2030, 1, 2, 12, tzinfo=dt_timezone.utc)
DESIRED = NOW + timedelta(days=1)


def api():
    return import_module("rides.services.matching_service")


@pytest.fixture
def scene(academic_user_factory, monkeypatch):
    monkeypatch.setattr(timezone, "now", lambda: NOW)
    driver = academic_user_factory(role="MOTORISTA", full_name="Motorista Sintético")
    passenger = academic_user_factory()
    for user in (driver, passenger):
        user.academic_status = "ATIVA"
        user.save(update_fields=["academic_status", "updated_at"])
    catalog = {p.code: p for p in RoutePoint.objects.all()}
    # IDs/names deliberately disagree with traversal order.
    points = [catalog[c] for c in (
        "terminal-norte", "campus-univille", "bairro-america", "terminal-central")]
    offer = RideOffer.objects.create(
        driver=driver, origin=points[0], destination=points[-1],
        departure_at=DESIRED, seats=3, vehicle_model="Veículo Sintético",
        vehicle_color="Azul", vehicle_plate="PRIVADA-123")
    Waypoint.objects.create(offer=offer, point=points[2], position=2)
    Waypoint.objects.create(offer=offer, point=points[1], position=1)
    return SimpleNamespace(driver=driver, passenger=passenger, points=points, offer=offer)


def query(scene, **overrides):
    values = dict(boarding_id=scene.points[0].pk, alighting_id=scene.points[-1].pk,
                  desired_at=DESIRED)
    values.update(overrides)
    return api().SearchQuery(**values)


@pytest.mark.parametrize("field", ["boarding_id", "alighting_id"])
@pytest.mark.parametrize("invalid", [None, True, False, 0, -1, 1.5, "1", ""])
def test_query_rejects_invalid_ids(field, invalid):
    values = dict(boarding_id=1, alighting_id=2, desired_at=DESIRED)
    values[field] = invalid
    with pytest.raises(ValidationError) as error:
        api().SearchQuery(**values)
    assert field in error.value.message_dict


@pytest.mark.parametrize("invalid", [None, "", "2030-01-01", datetime(2030, 1, 1)])
def test_query_requires_aware_datetime(invalid):
    with pytest.raises(ValidationError) as error:
        api().SearchQuery(boarding_id=1, alighting_id=2, desired_at=invalid)
    assert "desired_at" in error.value.message_dict


def test_query_distinct_immutable_and_no_future_requirement():
    with pytest.raises(ValidationError) as error:
        api().SearchQuery(boarding_id=1, alighting_id=1, desired_at=DESIRED)
    assert "alighting_id" in error.value.message_dict
    q = api().SearchQuery(boarding_id=1, alighting_id=2, desired_at=NOW-timedelta(days=1))
    with pytest.raises(FrozenInstanceError):
        q.boarding_id = 3


@pytest.mark.parametrize("boarding,alighting", list(product(range(4), repeat=2)))
@pytest.mark.django_db
def test_all_route_pairs(scene, boarding, alighting):
    if boarding == alighting:
        with pytest.raises(ValidationError):
            query(scene, boarding_id=scene.points[boarding].pk,
                  alighting_id=scene.points[alighting].pk)
        return
    q = query(scene, boarding_id=scene.points[boarding].pk,
              alighting_id=scene.points[alighting].pk)
    assert api().MatchingService.route_matches(scene.offer, q) is (boarding < alighting)
    results = api().MatchingService.search(passenger=scene.passenger, query=q)
    assert bool(results) is (boarding < alighting)


@pytest.mark.django_db
def test_direct_absent_and_ambiguous_routes(scene):
    scene.offer.waypoints.all().delete()
    assert api().MatchingService.route_matches(scene.offer, query(scene))
    assert not api().MatchingService.route_matches(
        scene.offer, query(scene, boarding_id=scene.points[1].pk))
    # Legacy malformed data can bypass model.clean; it must not be repaired by matching.
    Waypoint.objects.bulk_create([Waypoint(offer=scene.offer, point=scene.points[0], position=1)])
    assert not api().MatchingService.route_matches(scene.offer, query(scene))
    assert api().MatchingService.search(passenger=scene.passenger, query=query(scene)) == ()


@pytest.mark.parametrize("seconds,expected", [(-1801, False), (-1800, True), (0, True),
                                              (1800, True), (1801, False)])
def test_time_boundaries_and_midnight(seconds, expected):
    desired = datetime(2030, 1, 3, 0, 10, tzinfo=dt_timezone.utc)
    assert api().MatchingService.time_matches(desired+timedelta(seconds=seconds), desired) is expected


def test_equivalent_offsets_preserve_seconds():
    desired = DESIRED.astimezone(dt_timezone(timedelta(hours=-3)))
    assert api().MatchingService.time_matches(DESIRED+timedelta(minutes=30), desired)
    assert not api().MatchingService.time_matches(
        DESIRED+timedelta(minutes=30, microseconds=1), desired)


@pytest.mark.parametrize("seconds,expected", [(-1801, False), (-1800, True), (0, True),
                                              (1800, True), (1801, False)])
@pytest.mark.django_db
def test_search_applies_time_window(scene, seconds, expected):
    RideOffer.objects.filter(pk=scene.offer.pk).update(
        departure_at=DESIRED+timedelta(seconds=seconds))
    assert bool(api().MatchingService.search(passenger=scene.passenger,
                                             query=query(scene))) is expected


@pytest.mark.parametrize("offset,expected", [(-1, False), (0, False), (1, True)])
@pytest.mark.django_db
def test_departure_must_be_strictly_future(scene, offset, expected):
    RideOffer.objects.filter(pk=scene.offer.pk).update(departure_at=NOW+timedelta(seconds=offset))
    results = api().MatchingService.search(passenger=scene.passenger,
                                          query=query(scene, desired_at=NOW-timedelta(seconds=1)))
    assert bool(results) is expected


@pytest.mark.parametrize("subject", ["driver", "passenger"])
@pytest.mark.parametrize("changes", [
    {"academic_status": "PENDENTE"}, {"is_active": False}, {"role": "OTHER"},
])
@pytest.mark.django_db
def test_revalidates_current_accounts(scene, subject, changes):
    user = getattr(scene, subject)
    # Keep caller stale: authorization must read the current database.
    get_user_model().objects.filter(pk=user.pk).update(**changes)
    if subject == "passenger":
        with pytest.raises(PermissionDenied):
            api().MatchingService.search(passenger=user, query=query(scene))
    else:
        assert api().MatchingService.search(passenger=scene.passenger, query=query(scene)) == ()


@pytest.mark.django_db
def test_nonpassenger_and_anonymous_rejected(scene):
    from django.contrib.auth.models import AnonymousUser
    for user in (scene.driver, AnonymousUser(), SimpleNamespace(pk=999999999)):
        with pytest.raises(PermissionDenied):
            api().MatchingService.search(passenger=user, query=query(scene))


@pytest.mark.parametrize("field", ["boarding_id", "alighting_id"])
@pytest.mark.django_db
def test_unknown_catalog_points_are_field_errors(scene, field):
    with pytest.raises(ValidationError) as error:
        api().MatchingService.search(passenger=scene.passenger,
                                    query=query(scene, **{field: 999999999}))
    assert field in error.value.message_dict


@pytest.mark.django_db
def test_bad_query_type_is_rejected(scene):
    with pytest.raises(ValidationError):
        api().MatchingService.search(passenger=scene.passenger, query={})


@pytest.mark.django_db
def test_projection_immutable_ordered_and_read_only(scene):
    before = (list(RideOffer.objects.values()), list(Waypoint.objects.values()),
              list(get_user_model().objects.values()))
    results = api().MatchingService.search(passenger=scene.passenger, query=query(scene))
    assert isinstance(results, tuple) and len(results) == 1
    dto = results[0]
    assert {f.name for f in fields(dto)} == {
        "offer_id", "driver_display_name", "itinerary", "departure_at", "seats",
        "vehicle_model", "vehicle_color"}
    assert dto.driver_display_name == scene.driver.display_name
    assert dto.itinerary == tuple(p.name for p in scene.points)
    assert dto.departure_at == DESIRED and dto.seats == 3
    assert dto.vehicle_model == "Veículo Sintético" and dto.vehicle_color == "Azul"
    for secret in (scene.driver.full_name, scene.driver.email, scene.offer.vehicle_plate):
        assert secret not in repr(dto)
    with pytest.raises(FrozenInstanceError):
        dto.seats = 4
    assert (list(RideOffer.objects.values()), list(Waypoint.objects.values()),
            list(get_user_model().objects.values())) == before


@pytest.mark.django_db
def test_order_unique_no_n_plus_one_and_one_clock_read(scene, monkeypatch):
    def search_queries():
        with CaptureQueriesContext(connection) as captured:
            result = api().MatchingService.search(passenger=scene.passenger, query=query(scene))
        return result, len(captured)
    first, small = search_queries()
    ids = [scene.offer.pk]
    for index in range(4):
        offer = RideOffer.objects.create(
            driver=scene.driver, origin=scene.points[0], destination=scene.points[-1],
            departure_at=DESIRED-timedelta(minutes=index), seats=1,
            vehicle_model="Outro Sintético", vehicle_color="Verde", vehicle_plate="PRIVADO")
        Waypoint.objects.create(offer=offer, point=scene.points[1], position=1)
        ids.append(offer.pk)
    # Same departure; creation time precedes PK as tie-breaker.
    RideOffer.objects.filter(pk=ids[1]).update(created_at=NOW-timedelta(days=1))
    calls = []
    monkeypatch.setattr(timezone, "now", lambda: calls.append(1) or NOW)
    result, large = search_queries()
    assert calls == [1]
    assert large == small
    assert [r.offer_id for r in result] == [ids[4], ids[3], ids[2], ids[1], ids[0]]
    assert len({r.offer_id for r in result}) == len(result)
    assert connection.vendor == "postgresql"


@pytest.mark.django_db
def test_departure_origin_is_reference_even_for_intermediate_boarding(scene):
    q = query(scene, boarding_id=scene.points[1].pk, desired_at=DESIRED+timedelta(minutes=30))
    assert len(api().MatchingService.search(passenger=scene.passenger, query=q)) == 1

