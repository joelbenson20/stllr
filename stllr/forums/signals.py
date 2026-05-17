from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(m2m_changed, sender=Post.users_star.through)
def users_star_changed(sender, instance, **kwargs):
    total_stars = instance.users_star.count()
    # Distance is defined as the number of users that have not yet starred the page
    d = User.objects.count() - total_stars
    # If all users have liked, return the highest big integer to avoid dividing by 0
    if (d == 0):
        brightness = 1.0000000001
    # Otherwise, return the inverse squared value
    else:
        brightness = 1 / (d ** 2)
    Post.objects.filter(pk=instance.pk).update(total_stars=total_stars, brightness=brightness)