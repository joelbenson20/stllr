from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.conf import settings
from django.db import models
from django.db.models import Q

class User(AbstractUser):

    def get_full_name(self):
        return super().get_full_name()

    def get_contacts(self):
        """Returns a queryset of accepted contact Users (both directions)."""
        return type(self).objects.filter(
            Q(contacts_received__from_user=self, contacts_received__status=ContactRelation.Status.ACCEPTED) |
            Q(contacts_sent__to_user=self, contacts_sent__status=ContactRelation.Status.ACCEPTED)
        ).distinct()

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    background = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        blank=True
    )

    def get_absolute_url(self):
        return reverse("profile", kwargs={"username": self.user.username})
    
    def __str__(self):
        return f'Profile of {self.user.username}'
    
class ContactRelation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'

    from_user = models.ForeignKey(User, related_name='contacts_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='contacts_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

class Mute(models.Model):
    muter = models.ForeignKey(User, related_name='muting', on_delete=models.CASCADE)
    muted = models.ForeignKey(User, related_name='muted_by', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('muter', 'muted')

class Action(models.Model):
    class Verb(models.TextChoices):
        STARRED = 'starred', 'starred'
        POSTED = 'posted', 'posted to the forum'
        REPLIED = 'replied', 'replied in the forum'
        ENTERED = 'entered', 'entered the room'

    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    verb = models.CharField(max_length=20, choices=Verb.choices)
    object_ct = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name='actions',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object = GenericForeignKey('object_ct', 'object_id')

    created = models.DateTimeField(auto_now_add=True)
    removed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['object_ct', 'object_id']),
        ]

    def __str__(self):
        return f'{self.actor.username} {self.get_verb_display()} {self.object}'