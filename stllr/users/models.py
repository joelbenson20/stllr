from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django.db import models

class User(AbstractUser):

    def get_full_name(self):
        return super().get_full_name()

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    bio = models.CharField(blank=True)
    photo = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        blank=True
    )

    def get_absolute_url(self):
        return reverse("profile", kwargs={"username": self.user.username})
    
    def __str__(self):
        return f'Profile of {self.user.username}'
    
class Contact(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'

    from_user = models.ForeignKey(User, related_name='contacts_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='contacts_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

class Action(models.Model):
    class Verb(models.TextChoices):
        STARRED = 'starred', 'Starred'
        POSTED = 'posted', 'Posted'
        CHECKED_IN = 'checked_in', 'Checked In'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    verb = models.CharField(max_length=20, choices=Verb.choices)
    page = models.ForeignKey('pages.Page', null=True ,blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
    
    def __str__(self):
        return f'{self.user.username} {self.verb} {self.page}'