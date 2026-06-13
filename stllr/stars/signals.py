from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Star
from .tasks import update_brightnesses
from .utils import calculate_brightness

User = get_user_model()


@receiver(post_save, sender=Star)
@receiver(post_delete, sender=Star)
def update_total_stars(sender, instance, **kwargs):
    obj = instance.object
    obj.total_stars = obj.stars.count()
    obj.brightness = calculate_brightness(obj.total_stars, User.objects.count())
    obj.save(update_fields=['total_stars', 'brightness'])


@receiver(post_save, sender=User)
def update_brightnesses_on_user_create(sender, instance, created, **kwargs):
    if created:
        update_brightnesses.delay()