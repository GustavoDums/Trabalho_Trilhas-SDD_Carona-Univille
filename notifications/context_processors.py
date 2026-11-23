from django.utils.functional import SimpleLazyObject

from .models import Notification


def can_view_notifications(user):
    return user.is_authenticated and user.is_active and user.is_activated


def unread_notifications(request):
    user = getattr(request, "user", None)
    if user is None or not can_view_notifications(user):
        return {}

    unread = Notification.objects.filter(recipient_id=user.pk, read_at__isnull=True)
    return {"notification_unread_count": SimpleLazyObject(unread.count)}
