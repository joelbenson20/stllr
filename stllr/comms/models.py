from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    class Event(models.TextChoices):
        CONTACT_REQUEST = 'contact_request', 'Contact Request'
        POST_STARRED = 'post_starred', 'Post Starred'
        POST_REPLIED = 'post_replied', 'Post Replied'

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
        unique_together = ('recipient', 'event', 'object_ct', 'object_id')
        ordering = ['-updated']

    def __str__(self):
        return f'{self.recipient.username}: {self.verb}'
    
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
        unique_together = ('notification', 'actor')
        ordering = ['-created']