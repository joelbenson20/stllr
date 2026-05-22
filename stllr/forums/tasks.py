import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

STAR_LIFE = timedelta(days=7)

@shared_task(name="forum.update_post_brightnesses")
def update_post_brightnesses():
    from .models import Post
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_count = User.objects.count()

    posts = list(Post.objects.all())
    for post in posts:
        d = user_count - post.total_stars
        post.brightness = 1e15 if d == 0 else 1 / (d ** 2)

    Post.objects.bulk_update(posts, ['brightness'])
    return len(posts)

@shared_task(name="forum.delete_old_post_stars")
def delete_old_post_stars():
    from .models import PostStar

    cutoff = timezone.now() - STAR_LIFE
    for star in PostStar.objects.filter(created__lt=cutoff):
        star.delete()

    return