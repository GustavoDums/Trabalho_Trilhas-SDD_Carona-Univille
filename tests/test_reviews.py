"""Feature 006/T002 unificada — roadmap T028; REQ-008/REQ-003/REQ-017."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from importlib import import_module
from threading import Barrier
from unittest.mock import Mock

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, connections, transaction, close_old_connections
from django.db.models.deletion import ProtectedError

from rides.models import RideBooking, RideOffer


def service():
    return import_module('reviews.services.review_service').ReviewService


def model():
    return apps.get_model('reviews', 'RideReview')


def complete(scene, **overrides):
    args = dict(user=scene.driver, offer_id=scene.offer.pk,
                clock=lambda: scene.departure+timedelta(hours=1))
    args.update(overrides)
    return service().complete_offer(**args)


def review(scene, **overrides):
    args = dict(user=scene.passenger, offer_id=scene.offer.pk,
                reviewed_user_id=scene.driver.pk, rating=5,
                clock=lambda: scene.departure+timedelta(hours=2))
    args.update(overrides)
    return service().create_review(**args)


@pytest.mark.django_db
@pytest.mark.parametrize('rating', [1, 5])
def test_model_valid_rating_optional_comment_and_immutable_history(cancellation_scene, rating):
    scene = cancellation_scene
    complete(scene)
    result = review(scene, rating=rating, comment='  Comentário sintético  ')
    assert result.rating == rating and result.comment == 'Comentário sintético'
    assert result.created_at == scene.departure+timedelta(hours=2)
    result.comment = 'Alteração não permitida'
    with pytest.raises(ValidationError):
        result.save()
    result.refresh_from_db()
    assert result.comment == 'Comentário sintético'
    assert get_user_model().objects.get(pk=scene.driver.pk).academic_status == 'ATIVA'
    with pytest.raises(ProtectedError):
        result.offer.delete()


@pytest.mark.django_db
@pytest.mark.parametrize('rating', [0, 6, 1.5, True, '1.5', None])
def test_model_invalid_ratings_never_truncate(cancellation_scene, rating):
    scene = cancellation_scene
    complete(scene)
    with pytest.raises(ValidationError):
        review(scene, rating=rating)
    assert not model().objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize('comment', ['', 'x'*500, 'x'*501])
def test_comment_optional_and_exact_limit(cancellation_scene, comment):
    scene = cancellation_scene
    complete(scene)
    if len(comment) > 500:
        with pytest.raises(ValidationError):
            review(scene, comment=comment)
        assert not model().objects.exists()
    else:
        assert review(scene, comment=comment).comment == comment


@pytest.mark.django_db
@pytest.mark.parametrize('invalid', ['rating', 'self', 'duplicate'])
def test_database_constraints_protect_raw_insert(cancellation_scene, invalid):
    scene = cancellation_scene
    complete(scene)
    result = review(scene)
    values = dict(offer=scene.offer, reviewer=scene.driver, reviewed_user=scene.passenger,
                  rating=1, comment='', created_at=result.created_at)
    if invalid == 'rating':
        values['rating'] = 6
    elif invalid == 'self':
        values['reviewed_user'] = scene.driver
    else:
        values.update(reviewer=scene.passenger, reviewed_user=scene.driver)
    with pytest.raises(IntegrityError), transaction.atomic():
        model().objects.bulk_create([model()(**values)])
    assert model().objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize('seconds', [-1, 0, 1])
def test_completion_departure_border_and_idempotence(cancellation_scene, seconds):
    scene = cancellation_scene
    now = scene.departure+timedelta(seconds=seconds)
    clock = Mock(return_value=now)
    if seconds < 0:
        with pytest.raises(ValidationError):
            complete(scene, clock=clock)
        scene.offer.refresh_from_db()
        assert scene.offer.completed_at is None
    else:
        result = complete(scene, clock=clock)
        assert result.completed_at == now and result.status == 'ABERTA' and result.seats == 1
        repeat_clock = Mock(side_effect=AssertionError('Repetição não altera término'))
        assert complete(scene, clock=repeat_clock).completed_at == now
        repeat_clock.assert_not_called()
    clock.assert_called_once_with()


@pytest.mark.django_db
@pytest.mark.parametrize('actor', ['anonymous', 'passenger', 'third_driver', 'pending', 'disabled'])
def test_only_current_active_owner_can_complete(cancellation_scene, academic_user_factory, actor):
    scene = cancellation_scene
    user = scene.driver
    if actor == 'anonymous':
        user = AnonymousUser()
    elif actor == 'passenger':
        user = scene.passenger
    elif actor == 'third_driver':
        user = academic_user_factory(role='MOTORISTA', password=None)
        get_user_model().objects.filter(pk=user.pk).update(academic_status='ATIVA')
    elif actor == 'pending':
        get_user_model().objects.filter(pk=user.pk).update(academic_status='PENDENTE')
    else:
        get_user_model().objects.filter(pk=user.pk).update(is_active=False)
    with pytest.raises(PermissionDenied):
        complete(scene, user=user)


@pytest.mark.django_db
@pytest.mark.parametrize('offset,accepted', [(-1, False), (0, True), (1, True),
                                           (48*3600, True), (48*3600+1, False)])
def test_closed_review_window_uses_completion_not_departure(cancellation_scene, offset, accepted):
    scene = cancellation_scene
    end = complete(scene).completed_at
    clock = Mock(return_value=end+timedelta(seconds=offset))
    if accepted:
        assert review(scene, clock=clock).created_at == end+timedelta(seconds=offset)
    else:
        with pytest.raises(ValidationError):
            review(scene, clock=clock)
        assert not model().objects.exists()
    clock.assert_called_once_with()


@pytest.mark.django_db
@pytest.mark.parametrize('state', ['legacy', 'cancelled_offer', 'cancelled_booking', 'no_show'])
def test_missing_completion_cancelled_and_no_show_cannot_review(cancellation_scene, state):
    scene = cancellation_scene
    if state != 'legacy':
        complete(scene)
    if state == 'cancelled_offer':
        # Estado legado: CANCELADA sem conclusão; não inventar conclusão.
        RideOffer.objects.filter(pk=scene.offer.pk).update(completed_at=None, status='CANCELADA')
    elif state == 'cancelled_booking':
        RideBooking.objects.filter(pk=scene.booking.pk).update(status='CANCELADA')
    elif state == 'no_show':
        RideBooking.objects.filter(pk=scene.booking.pk).update(no_show_at=scene.departure)
    with pytest.raises(ValidationError):
        review(scene)
    assert not model().objects.exists()
    if state == 'cancelled_offer':
        with pytest.raises(ValidationError):
            complete(scene)


@pytest.mark.django_db
@pytest.mark.parametrize('actor', ['anonymous', 'other', 'self', 'passenger_pair', 'pending', 'disabled_target'])
def test_review_requires_current_eligible_counterparts(cancellation_scene, actor):
    scene = cancellation_scene
    complete(scene)
    args = {}
    if actor == 'anonymous':
        args['user'] = AnonymousUser()
    elif actor == 'other':
        args['user'] = scene.other
    elif actor == 'self':
        args['reviewed_user_id'] = scene.passenger.pk
    elif actor == 'passenger_pair':
        args['reviewed_user_id'] = scene.other.pk
    elif actor == 'pending':
        get_user_model().objects.filter(pk=scene.passenger.pk).update(academic_status='PENDENTE')
    else:
        get_user_model().objects.filter(pk=scene.driver.pk).update(is_active=False)
    with pytest.raises((PermissionDenied, ValidationError)):
        review(scene, **args)
    assert not model().objects.exists()


@pytest.mark.django_db
def test_mutual_reviews_and_duplicate_rejection(cancellation_scene):
    scene = cancellation_scene
    complete(scene)
    first = review(scene)
    second = review(scene, user=scene.driver, reviewed_user_id=scene.passenger.pk, rating=1)
    assert first.pk != second.pk and model().objects.count() == 2
    before = list(model().objects.values())
    with pytest.raises(ValidationError):
        review(scene, rating=1)
    assert list(model().objects.values()) == before


@pytest.mark.django_db
@pytest.mark.parametrize('target', ['offer_id', 'reviewed_user_id'])
@pytest.mark.parametrize('invalid', [True, 0, '1', 999999])
def test_service_rejects_invalid_ids(cancellation_scene, target, invalid):
    scene = cancellation_scene
    complete(scene)
    with pytest.raises(ValidationError):
        review(scene, **{target: invalid})
    assert not model().objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize('operation', ['complete', 'review'])
def test_naive_clock_is_rejected_without_state_change(cancellation_scene, operation):
    scene = cancellation_scene
    if operation == 'review':
        complete(scene)
    with pytest.raises(ValidationError):
        (complete if operation == 'complete' else review)(
            scene, clock=lambda: scene.departure.replace(tzinfo=None))
    assert not model().objects.exists()


@pytest.mark.django_db
def test_auditless_review_failure_rolls_back_insert(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    complete(scene)
    original = model().save
    def fail_after_insert(self, *args, **kwargs):
        original(self, *args, **kwargs)
        raise RuntimeError('Falha sintética após avaliação')
    with monkeypatch.context() as patch:
        patch.setattr(model(), 'save', fail_after_insert)
        with pytest.raises(RuntimeError):
            review(scene)
    assert not model().objects.exists()
    assert review(scene).rating == 5


@pytest.mark.django_db(transaction=True)
def test_duplicate_reviews_serialize_independent_postgresql_transactions(cancellation_scene, record_testsuite_property):
    import json
    scene = cancellation_scene
    complete(scene)
    assert connection.vendor == 'postgresql' and not connection.in_atomic_block
    barrier = Barrier(2, timeout=10)
    def worker():
        close_old_connections()
        try:
            try:
                with transaction.atomic():
                    with connections['default'].cursor() as cursor:
                        cursor.execute("SET LOCAL lock_timeout = '10s'")
                        cursor.execute('SELECT pg_backend_pid(), txid_current()')
                        pid, txid = cursor.fetchone()
                    barrier.wait()
                    review(scene)
                return 'created', pid, txid
            except ValidationError:
                return 'duplicate', pid, txid
        finally:
            connections['default'].close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(worker) for _ in range(2)]
        outcomes = [f.result(timeout=20) for f in futures]
    assert sorted(item[0] for item in outcomes) == ['created', 'duplicate']
    assert len({item[1] for item in outcomes}) == len({item[2] for item in outcomes}) == 2
    assert model().objects.count() == 1
    record_testsuite_property('review_duplicate_race', json.dumps(outcomes))


@pytest.mark.django_db
def test_model_allows_noop_save_without_changing_history(cancellation_scene):
    scene = cancellation_scene
    complete(scene)
    result = review(scene)
    before = list(model().objects.values())
    result.save()
    assert list(model().objects.values()) == before


@pytest.mark.django_db
@pytest.mark.parametrize('field', ['rating', 'comment'])
def test_model_validation_supports_excluded_fields_for_future_modelform(cancellation_scene, field):
    scene = cancellation_scene
    result = model()(offer=scene.offer, reviewer=scene.passenger, reviewed_user=scene.driver,
                     rating=None if field == 'rating' else 5,
                     comment=None if field == 'comment' else '')
    # ModelForm exclui campo inválido antes de validar os demais; não gravar esse objeto.
    result.full_clean(exclude=[field])
    assert result.pk is None and not model().objects.exists()


@pytest.mark.django_db
def test_null_comment_is_not_silently_coerced(cancellation_scene):
    scene = cancellation_scene
    complete(scene)
    with pytest.raises(ValidationError):
        review(scene, comment=None)
    assert not model().objects.exists()


@pytest.mark.django_db
def test_completion_and_no_show_schema_constraints_preserve_legacy(cancellation_scene):
    scene = cancellation_scene
    scene.offer.refresh_from_db()
    scene.booking.refresh_from_db()
    assert scene.offer.completed_at is None and scene.booking.no_show_at is None
    with pytest.raises(IntegrityError), transaction.atomic():
        RideOffer.objects.filter(pk=scene.offer.pk).update(completed_at=scene.departure-timedelta(seconds=1))
    with pytest.raises(IntegrityError), transaction.atomic():
        RideOffer.objects.filter(pk=scene.offer.pk).update(completed_at=scene.departure, status='CANCELADA')
    scene.booking.no_show_at = scene.departure.replace(tzinfo=None)
    with pytest.raises(ValidationError):
        scene.booking.save()
    assert model()._meta.get_field('comment').max_length == 500
    for field in ('offer', 'reviewer', 'reviewed_user'):
        assert model()._meta.get_field(field).remote_field.on_delete.__name__ == 'PROTECT'


# Feature 006/T004 unificada — roadmap T029.
def review_form(data=None):
    return import_module('reviews.forms').RideReviewForm(data=data)


def review_url(scene, **overrides):
    from django.urls import reverse
    args = dict(offer_id=scene.offer.pk, reviewed_id=scene.driver.pk)
    args.update(overrides)
    return reverse('reviews:submit_review', kwargs=args)


@pytest.fixture
def web_review_scene(cancellation_scene, monkeypatch):
    scene = cancellation_scene
    complete(scene)
    monkeypatch.setattr('reviews.services.review_service.timezone.now',
                        lambda: scene.departure+timedelta(hours=2))
    return scene


@pytest.mark.parametrize('rating', [1, 5])
def test_form_only_rating_and_optional_comment(rating):
    form = review_form({'rating': rating})
    assert set(form.fields) == {'rating', 'comment'}
    assert form.is_valid(), form.errors
    assert form.cleaned_data == {'rating': rating, 'comment': ''}


@pytest.mark.parametrize('rating', ['', 0, 6, '1.5', True, 'abc'])
def test_form_rejects_invalid_rating(rating):
    form = review_form({'rating': rating})
    assert not form.is_valid() and 'rating' in form.errors


@pytest.mark.parametrize('length,valid', [(500, True), (501, False)])
def test_form_comment_limit(length, valid):
    form = review_form({'rating': 5, 'comment': 'x'*length})
    assert form.is_valid() is valid


@pytest.mark.django_db
def test_http_review_get_is_authorized_minimal_and_read_only(web_review_scene):
    from django.test import Client
    scene = web_review_scene
    client = Client(enforce_csrf_checks=True)
    client.force_login(scene.passenger)
    before = (list(RideOffer.objects.values()), list(RideBooking.objects.values()), list(model().objects.values()))
    response = client.get(review_url(scene))
    assert response.status_code == 200
    assert response.context['form'].is_bound is False
    assert 'csrfmiddlewaretoken' in response.content.decode()
    assert scene.driver.full_name not in response.content.decode()
    assert scene.driver.email not in response.content.decode() and scene.offer.vehicle_plate not in response.content.decode()
    assert before == (list(RideOffer.objects.values()), list(RideBooking.objects.values()), list(model().objects.values()))
    assert set(response.context['review_context']) == {'counterpart_name', 'departure_at', 'completed_at'}


@pytest.mark.django_db
@pytest.mark.parametrize('driver_view', [False, True])
def test_http_review_submission_real_csrf_identity_and_fixed_redirect(web_review_scene, driver_view):
    from django.test import Client
    scene = web_review_scene
    actor, target = (scene.driver, scene.passenger) if driver_view else (scene.passenger, scene.driver)
    client = Client(enforce_csrf_checks=True)
    client.force_login(actor)
    url = review_url(scene, reviewed_id=target.pk)
    assert client.get(url).status_code == 200
    response = client.post(url, dict(
        csrfmiddlewaretoken=client.cookies['csrftoken'].value, rating=5, comment='Ótima viagem sintética',
        reviewer=scene.other.pk, reviewed_user=scene.other.pk, offer_id=999999,
        created_at='1999-01-01T00:00:00Z', next='https://example.invalid/'))
    assert response.status_code == 302 and response.url == '/accounts/profile/'
    result = model().objects.get()
    assert result.reviewer_id == actor.pk and result.reviewed_user_id == target.pk
    assert result.offer_id == scene.offer.pk and result.created_at == scene.departure+timedelta(hours=2)
    assert result.rating == 5 and result.comment == 'Ótima viagem sintética'
    before = list(model().objects.values())
    repeated = client.post(url, {'csrfmiddlewaretoken': client.cookies['csrftoken'].value, 'rating': 1})
    assert repeated.status_code == 400 and list(model().objects.values()) == before
    assert 'Não foi possível' in repeated.content.decode()


@pytest.mark.django_db
def test_http_review_real_login_then_submit(web_review_scene):
    from django.test import Client
    scene = web_review_scene
    scene.passenger.set_password('Ficticia!Rota-2026#')
    scene.passenger.save(update_fields=['password'])
    client = Client(enforce_csrf_checks=True)
    client.get('/accounts/login/')
    response = client.post('/accounts/login/', {
        'email': scene.passenger.email, 'password': 'Ficticia!Rota-2026#',
        'csrfmiddlewaretoken': client.cookies['csrftoken'].value})
    assert response.status_code == 302 and response.url == '/accounts/profile/'
    url = review_url(scene)
    assert client.get(url).status_code == 200
    response = client.post(url, {'rating': 1, 'csrfmiddlewaretoken': client.cookies['csrftoken'].value})
    assert response.status_code == 302
    assert model().objects.get().reviewer_id == scene.passenger.pk


@pytest.mark.django_db
@pytest.mark.parametrize('token', [None, 'invalid'])
def test_http_review_csrf_required(web_review_scene, token):
    from django.test import Client
    scene = web_review_scene
    client = Client(enforce_csrf_checks=True)
    client.force_login(scene.passenger)
    payload = {'rating': 5}
    if token:
        payload['csrfmiddlewaretoken'] = token
    assert client.post(review_url(scene), payload).status_code == 403
    assert not model().objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize('method', ['put', 'patch', 'delete', 'head', 'options'])
def test_http_review_other_methods_405(web_review_scene, method):
    from django.test import Client
    scene = web_review_scene
    client = Client()
    client.force_login(scene.passenger)
    response = getattr(client, method)(review_url(scene))
    assert response.status_code == 405 and response.headers['Allow'] == 'GET, POST'
    assert not model().objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize('identity', ['anonymous', 'pending', 'disabled', 'third_party', 'inactive_target'])
@pytest.mark.parametrize('method', ['get', 'post'])
def test_http_review_authorization_no_target_leak(web_review_scene, identity, method):
    from django.test import Client
    scene = web_review_scene
    actor = scene.passenger
    if identity == 'third_party':
        actor = scene.other
    elif identity == 'pending':
        get_user_model().objects.filter(pk=actor.pk).update(academic_status='PENDENTE')
    elif identity == 'disabled':
        get_user_model().objects.filter(pk=actor.pk).update(is_active=False)
    elif identity == 'inactive_target':
        get_user_model().objects.filter(pk=scene.driver.pk).update(is_active=False)
    client = Client()
    if identity != 'anonymous':
        client.force_login(actor)
    response = getattr(client, method)(review_url(scene), {'rating': 5})
    expected = 302 if identity in ('anonymous', 'pending', 'disabled') else (400 if identity == 'third_party' else 403)
    assert response.status_code == expected
    html = response.content.decode()
    assert scene.driver.full_name not in html and scene.driver.email not in html
    assert scene.offer.vehicle_plate not in html and not model().objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize('state', ['legacy', 'cancelled', 'no_show', 'expired', 'before_completion', 'duplicate', 'missing'])
def test_http_review_get_and_post_revalidate_eligibility(web_review_scene, monkeypatch, state):
    from django.test import Client
    scene = web_review_scene
    url = review_url(scene)
    if state == 'legacy':
        RideOffer.objects.filter(pk=scene.offer.pk).update(completed_at=None)
    elif state == 'cancelled':
        RideBooking.objects.filter(pk=scene.booking.pk).update(status='CANCELADA')
    elif state == 'no_show':
        RideBooking.objects.filter(pk=scene.booking.pk).update(no_show_at=scene.departure)
    elif state in ('expired', 'before_completion'):
        at = scene.departure+timedelta(hours=49, seconds=1) if state == 'expired' else scene.departure
        monkeypatch.setattr('reviews.services.review_service.timezone.now', lambda: at)
    elif state == 'duplicate':
        review(scene)
    else:
        url = review_url(scene, offer_id=999999)
    before = list(model().objects.values())
    client = Client()
    client.force_login(scene.passenger)
    for method in ('get', 'post'):
        response = getattr(client, method)(url, {'rating': 5})
        assert response.status_code == 400
        assert '<form' not in response.content.decode()
        assert scene.driver.full_name not in response.content.decode()
    assert list(model().objects.values()) == before


@pytest.mark.django_db
def test_http_review_invalid_form_preserves_escaped_input_and_no_write(web_review_scene):
    from django.test import Client
    scene = web_review_scene
    client = Client()
    client.force_login(scene.passenger)
    response = client.post(review_url(scene), {'rating': 0, 'comment': '<script>alert(1)</script>'})
    assert response.status_code == 400
    html = response.content.decode()
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert 'rating' in response.context['form'].errors and not model().objects.exists()


@pytest.mark.django_db
def test_http_review_rechecks_after_get_before_post(web_review_scene):
    from django.test import Client
    scene = web_review_scene
    client = Client()
    client.force_login(scene.passenger)
    url = review_url(scene)
    assert client.get(url).status_code == 200
    RideBooking.objects.filter(pk=scene.booking.pk).update(status='CANCELADA')
    assert client.post(url, {'rating': 5}).status_code == 400
    assert not model().objects.exists()


@pytest.mark.django_db(transaction=True)
def test_http_review_concurrent_duplicate_post(web_review_scene, record_testsuite_property):
    import json
    from django.test import Client
    scene = web_review_scene
    url = review_url(scene)
    barrier = Barrier(2, timeout=10)
    assert connection.vendor == 'postgresql' and not connection.in_atomic_block
    def worker():
        close_old_connections()
        try:
            client = Client(enforce_csrf_checks=True)
            client.force_login(get_user_model().objects.get(pk=scene.passenger.pk))
            assert client.get(url).status_code == 200
            with transaction.atomic():
                with connections['default'].cursor() as cursor:
                    cursor.execute("SET LOCAL lock_timeout = '10s'")
                    cursor.execute('SELECT pg_backend_pid(), txid_current()')
                    pid, txid = cursor.fetchone()
                barrier.wait()
                response = client.post(url, {'rating': 5, 'csrfmiddlewaretoken': client.cookies['csrftoken'].value})
                status = response.status_code
            return status, pid, txid
        finally:
            connections['default'].close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(worker) for _ in range(2)]
        outcomes = [future.result(timeout=20) for future in futures]
    assert sorted(item[0] for item in outcomes) == [302, 400]
    assert len({item[1] for item in outcomes}) == len({item[2] for item in outcomes}) == 2
    assert model().objects.count() == 1
    record_testsuite_property('review_http_duplicate_race', json.dumps(outcomes))


@pytest.mark.django_db
def test_http_review_revalidation_during_post_refuses_changed_booking(web_review_scene, monkeypatch):
    from django.test import Client
    scene = web_review_scene
    original = service().review_context
    def change_after_check(**kwargs):
        context = original(**kwargs)
        RideBooking.objects.filter(pk=scene.booking.pk).update(status='CANCELADA')
        return context
    monkeypatch.setattr(service(), 'review_context', change_after_check)
    client = Client()
    client.force_login(scene.passenger)
    response = client.post(review_url(scene), {'rating': 5})
    assert response.status_code == 400 and not model().objects.exists()
    assert '<form' not in response.content.decode()
