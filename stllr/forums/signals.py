from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PostStar


@receiver(post_save, sender=PostStar)
@receiver(post_delete, sender=PostStar)
def update_post_total_stars(sender, instance, **kwargs):
    post = instance.post
    post.total_stars = post.stars.count()
    post.save(update_fields=['total_stars'])
