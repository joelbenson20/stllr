import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

STAR_LIFE = timedelta(days=7)

@shared_task(name="forum.delete_old_comment_stars")
def delete_old_comment_stars():
    from .models import CommentStar

    cutoff = timezone.now() - STAR_LIFE
    deleted_count, _ = CommentStar.objects.filter(created__lt=cutoff).delete()
    logger.info("Deleted %d CommentStar rows older than %s", deleted_count, cutoff.isoformat())
    return deleted_count