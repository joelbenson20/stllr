from django.db.models.signals import pre_save, post_save
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
        recipient=instance.post.author,
        event=Notification.Event.POST_STARRED,
        object=instance.post,
        actor=instance.user
    )

@receiver(post_save, sender=Post)
def notify_post_replied(sender, instance, created, **kwargs):
    if not created or instance.parent is None:
        return
    notify(
        recipient=instance.parent.author,
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

# Done by Claude, requires review
@receiver(pre_save, sender=Contact)
def track_contact_status(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_status = Contact.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
    else:
        instance._previous_status = None

@receiver(post_save, sender=Contact)
def notify_contact_accepted(sender, instance, created, **kwargs):
    if created:
        return
    if getattr(instance, '_previous_status', None) == Contact.Status.PENDING and instance.status == Contact.Status.ACCEPTED:
        notify(
            recipient=instance.from_user,
            event=Notification.Event.CONTACT_ACCEPTED,
            object=instance,
            actor=instance.to_user
        )