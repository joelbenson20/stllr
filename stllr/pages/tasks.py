import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber

logger = logging.getLogger(__name__)

STAR_LIFE = timedelta(days=7)

@shared_task(name="pages.delete_old_page_stars")
def delete_old_page_stars():
    from .models import PageStar

    cutoff = timezone.now() - STAR_LIFE
    for star in PageStar.objects.filter(created__lt=cutoff):
        star.delete()

    return

@shared_task(name="pages.update_page_brightnesses")
def update_page_brightnesses():
    from .models import Page
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user_count = User.objects.count()

    pages = list(Page.objects.all())
    for page in pages:
        d = user_count - page.total_stars
        page.brightness = 1e15 if d == 0 else 1 / (d ** 2)

    Page.objects.bulk_update(pages, ['brightness'])
    return len(pages)

@shared_task(name="pages.update_brightness_index")
def update_brightness_index():
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
    
    return