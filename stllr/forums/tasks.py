import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

STAR_LIFE = timedelta(days=7)

@shared_task(name="forum.delete_old_post_stars")
def delete_old_post_stars():
    from .models import PostStar

    cutoff = timezone.now() - STAR_LIFE
    deleted_count, _ = PostStar.objects.filter(created__lt=cutoff).delete()
    logger.info("Deleted %d PostStar rows older than %s", deleted_count, cutoff.isoformat())
    return deleted_count