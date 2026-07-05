import logging
from datetime import timedelta
from celery import shared_task
from django.core.cache import cache
from django.db.models import OrderBy
from django.db.models.expressions import RawSQL, Window
from django.db.models.functions import RowNumber
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="pages.update_rising_scores")
def update_rising_scores():
    from .models import Page

    pages = list(
        Page.objects.annotate(
            new_brightness_index=Window(expression=RowNumber(), order_by=['-brightness', OrderBy(RawSQL('RANDOM()', []))])
        )
    )
    for page in pages:
        page.rising_score = page.brightness_index - page.new_brightness_index
        page.brightness_index = page.new_brightness_index
    Page.objects.bulk_update(pages, ['rising_score', 'brightness_index'])


@shared_task(name="pages.update_forging_scores")
def update_forging_scores():
    from .models import Page
    from django.db.models import Count, Q

    cutoff = timezone.now() - timedelta(hours=24)
    pages = list(
        Page.objects.annotate(
            recent_post_count=Count('posts', filter=Q(posts__created__gte=cutoff))
        )
    )
    max_count = max((p.recent_post_count for p in pages), default=0)
    for page in pages:
        page.forging_score = page.recent_post_count / max_count if max_count else 0.0
    Page.objects.bulk_update(pages, ['forging_score'])
    return {'pages': len(pages)}


@shared_task(name="pages.update_poppin_scores")
def update_poppin_scores():
    from .models import Page

    pages = list(Page.objects.only('pk', 'poppin_score'))
    counts = {page.pk: len(cache.get(f'presence:room_{page.pk}') or {}) for page in pages}
    max_count = max(counts.values(), default=0)
    for page in pages:
        page.poppin_score = counts[page.pk] / max_count if max_count else 0.0
    Page.objects.bulk_update(pages, ['poppin_score'])
    return {'pages': len(pages)}
