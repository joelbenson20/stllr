from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Comment


@receiver(m2m_changed, sender=Comment.users_star.through)
def users_star_changed(sender, instance, **kwargs):
    instance.total_stars = instance.users_star.count()
    instance.save()