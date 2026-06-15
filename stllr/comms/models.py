from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    class Event(models.TextChoices):
        CONTACT_REQUEST = 'contact_request', 'Contact Request'
        CONTACT_ACCEPTED = 'contact_accepted', 'Contact Accepted'
        POST_STARRED = 'post_starred', 'Post Starred'
        POST_REPLIED = 'post_replied', 'Post Replied'
        POST_SHARED = 'post_shared', 'Post Shared'
        PAGE_SHARED = 'page_shared', 'Page Shared'
        PAGE_ALSO_STARRED = 'page_also_starred', 'Page Also Starred'
        POST_ALSO_STARRED = 'post_also_starred', 'Post Also Starred'
        CREW_INVITE = 'crew_invite', 'Crew Invite'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    event = models.CharField(max_length=30, choices=Event.choices)
    object_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object = GenericForeignKey('object_ct', 'object_id')
    actors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='NotificationActor'
    )
    actor_count = models.PositiveIntegerField(default=0)
    read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipient', 'event', 'object_ct', 'object_id'], name='unique_notification_per_recipient_event_object'),
        ]
        ordering = ['-updated']

    def __str__(self):
        return f'{self.recipient.username}: {self.event}'
    
class NotificationActor(models.Model):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='notification_actors'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_actor_entries'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['notification', 'actor'], name='unique_actor_per_notification'),
        ]
        ordering = ['-created']