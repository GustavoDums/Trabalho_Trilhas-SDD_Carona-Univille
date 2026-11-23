from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RideReview
from .services.reputation_service import ReputationService


@receiver(post_save, sender=RideReview, dispatch_uid='reviews.rebuild_reputation')
def rebuild_reputation_after_review(sender, instance, created, raw, **kwargs):
    if created and not raw:
        ReputationService.rebuild(user_id=instance.reviewed_user_id)
