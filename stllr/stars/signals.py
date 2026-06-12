from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Star


@receiver(post_save, sender=Star)
@receiver(post_delete, sender=Star)
def update_total_stars(sender, instance, **kwargs): #TODO: Update brightness immediately too. Right now it is a crontab task.
    obj = instance.object
    obj.total_stars = obj.stars.count()
    obj.save(update_fields=['total_stars'])
