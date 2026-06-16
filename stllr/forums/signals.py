import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Post, Mention
from crews.models import Crew

MENTION_RE = re.compile(r'@(\w+)')


@receiver(post_save, sender=Post)
def sync_mentions(sender, instance, **kwargs):
    handles = set(MENTION_RE.findall(instance.content))

    instance.mentions.all().delete()

    if not handles:
        return

    User = get_user_model()
    users = User.objects.filter(username__in=handles)
    crews = Crew.objects.filter(handle__in=handles)

    Mention.objects.bulk_create(
        [Mention(post=instance, user=u) for u in users] +
        [Mention(post=instance, crew=c) for c in crews]
    )
