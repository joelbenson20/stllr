import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber

logger = logging.getLogger(__name__)

STAR_LIFE_TIME = timedelta(days=7)

@shared_task(name="pages.delete_old_page_stars")
def delete_old_page_stars():
    """
    Delete Page Stars whose `created` timestamp is older than one week.

    Returns the number of rows deleted, which Celery records as the task
    result so it shows up in monitoring tools (Flower, etc.).
    """
    from .models import PageStar
    
    cutoff = timezone.now() - STAR_LIFE_TIME
    deleted_count, _ = PageStar.objects.filter(created__lt=cutoff).delete()
    logger.info("Deleted %d PageStar rows older than %s", deleted_count, cutoff.isoformat())
    return deleted_count

@shared_task(name="pages.update_brightness_index")
def update_brightness_index():
    """
    Update 'brightness_index' and 'rise' for each page.
    Returns success or failure message.
    """
    from .models import Page
    from django.db.models import OrderBy
    from django.db.models.expressions import RawSQL

    pages = Page.objects.annotate(
        new_brightness_index=Window(expression=RowNumber(), order_by=['-brightness', OrderBy(RawSQL('RANDOM()', []))])
    )
    pages = list(pages)

    for page in pages:
        page.rise = page.brightness_index - page.new_brightness_index
        page.brightness_index = page.new_brightness_index

    Page.objects.bulk_update(pages, ['rise', 'brightness_index'])
    logger.info("Updated the brightness index.")
    return