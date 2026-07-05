import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from .utils import calculate_brightness

logger = logging.getLogger(__name__)


@shared_task(name="stars.delete_old_stars")
def delete_old_stars():
    from .models import Star
    
    STAR_LIFE = timedelta(days=7)

    cutoff = timezone.now() - STAR_LIFE
    Star.objects.filter(created__lt=cutoff).delete()


@shared_task(name="stars.update_brightnesses")
def update_brightnesses():
    from pages.models import Page
    from forums.models import Post
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user_count = User.objects.count()

    pages = list(Page.objects.all())
    for page in pages:
        page.brightness = calculate_brightness(page.total_stars, user_count)
    Page.objects.bulk_update(pages, ['brightness'])

    posts = list(Post.objects.all())
    for post in posts:
        post.brightness = calculate_brightness(post.total_stars, user_count)
    Post.objects.bulk_update(posts, ['brightness'])

    return {'pages': len(pages), 'posts': len(posts)}
