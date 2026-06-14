from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from forums.models import Post
from pages.models import Page
from stars.models import Star
from users.models import ContactRelation
from .models import Notification
from .notifications import notify


@receiver(post_save, sender=Star)
def notify_starred(sender, instance, created, **kwargs):
    if not created:
        return
    obj = instance.object
    if isinstance(obj, Post):
        notify(
            recipient=obj.author,
            event=Notification.Event.POST_STARRED,
            object=obj,
            actor=instance.user
        )


@receiver(post_save, sender=Star)
def notify_also_starred(sender, instance, created, **kwargs):
    if not created:
        return
    obj = instance.object
    contacts = instance.user.get_contacts()
    prior_starrers = contacts.filter(
        stars__object_ct=instance.object_ct,
        stars__object_id=instance.object_id,
    ).exclude(pk=instance.user.pk)

    if isinstance(obj, Page):
        event = Notification.Event.PAGE_ALSO_STARRED
    elif isinstance(obj, Post):
        event = Notification.Event.POST_ALSO_STARRED
    else:
        return

    for contact in prior_starrers:
        notify(recipient=contact, event=event, object=obj, actor=instance.user)


@receiver(post_save, sender=Post)
def notify_post_replied(sender, instance, created, **kwargs):
    if not created or instance.parent is None or instance.author == instance.parent.author:
        return
    notify(
        recipient=instance.parent.author,
        event=Notification.Event.POST_REPLIED,
        object=instance.parent,
        actor=instance.author
    )

@receiver(post_save, sender=ContactRelation)
def notify_contact_request(sender, instance, created, **kwargs):
    if not created or instance.status != ContactRelation.Status.PENDING:
        return
    notify(
        recipient=instance.to_user,
        event=Notification.Event.CONTACT_REQUEST,
        object=instance,
        actor=instance.from_user
    )

@receiver(pre_save, sender=ContactRelation)
def track_contact_status(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_status = ContactRelation.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
    else:
        instance._previous_status = None

@receiver(post_save, sender=ContactRelation)
def notify_contact_accepted(sender, instance, created, **kwargs):
    if created:
        return
    if getattr(instance, '_previous_status', None) == ContactRelation.Status.PENDING and instance.status == ContactRelation.Status.ACCEPTED:
        notify(
            recipient=instance.from_user,
            event=Notification.Event.CONTACT_ACCEPTED,
            object=instance,
            actor=instance.to_user
        )
