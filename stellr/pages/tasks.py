import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

# Anything older than this is considered stale and gets deleted.
STAR_LIFE_TIME = timedelta(days=7)

@shared_task(name="pages.delete_old_page_stars")
def delete_old_page_stars():
    """Delete Page Stars whose `created` timestamp is older than one week.

    Returns the number of rows deleted, which Celery records as the task
    result so it shows up in monitoring tools (Flower, etc.).
    """
    from .models import PageStar
    
    cutoff = timezone.now() - STAR_LIFE_TIME
    deleted_count, _ = PageStar.objects.filter(created__lt=cutoff).delete()
    logger.info("Deleted %d PostStar rows older than %s", deleted_count, cutoff.isoformat())
    return deleted_count