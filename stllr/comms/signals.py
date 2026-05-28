from django.db.models.signals import post_save
from django.dispatch import receiver
from forums.models import Post, PostStar
from users.models import Contact
from .models import Notification
from .notifications import notify

@receiver(post_save, sender=PostStar)
def notify_post_starred(sender, instance, created, **kwargs):
    if not created:
        return
    notify(
        recipient=instance.post.user,
        event=Notification.Event.POST_STARRED,
        object=instance.post,
        actor=instance.user
    )

@receiver(post_save, sender=Post)
def notify_post_replied(sender, instance, created, **kwargs):
    if not created or instance.parent is None:
        return
    notify(
        recipient=instance.parent.user,
        event=Notification.Event.POST_REPLIED,
        object=instance.parent,
        actor=instance.user
    )

@receiver(post_save, sender=Contact)
def notify_contact_request(sender, instance, created, **kwargs):
    if not created or instance.status != Contact.Status.PENDING:
        return
    notify(
        recipient=instance.to_user,
        event=Notification.Event.CONTACT_REQUEST,
        object=instance,
        actor=instance.from_user
    )