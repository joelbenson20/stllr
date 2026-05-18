from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Post

@receiver(m2m_changed, sender=Post.users_star.through)
def update_brightness_on_star_change(sender, instance, action, **kwargs):
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return
    User = get_user_model()
    post = instance
    total_stars = post.users_star.count()
    d = User.objects.count() - total_stars
    brightness = 1e15 if d == 0 else 1 / (d ** 2)
    Post.objects.filter(pk=post.pk).update(total_stars=total_stars, brightness=brightness)
