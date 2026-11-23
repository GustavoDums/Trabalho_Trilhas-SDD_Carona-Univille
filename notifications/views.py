from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import ListView, View

from .context_processors import can_view_notifications
from .models import Notification


class NotificationAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/accounts/login/"

    def test_func(self):
        return can_view_notifications(self.request.user)


@method_decorator(never_cache, name="dispatch")
class NotificationListView(NotificationAccessMixin, ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return (
            Notification.objects.filter(recipient_id=self.request.user.pk)
            .only("kind", "created_at", "read_at")
            .annotate(offer_reference=Coalesce("booking__offer_id", "cancellation__offer_id"))
        )


class MarkNotificationReadView(NotificationAccessMixin, View):
    def post(self, request, notification_id):
        owned = Notification.objects.filter(pk=notification_id, recipient_id=request.user.pk)
        marked = owned.filter(read_at__isnull=True).update(read_at=timezone.now())
        if not marked and not owned.exists():
            raise Http404
        return redirect("notifications:list")
