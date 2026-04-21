from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django.db import models
from comments.models import Comment

class User(AbstractUser):
    
    @property
    def voted_comments(self):
        return Comment.objects.filter(votes__user=self)
    @property
    def voted_comments_ids(self):
        return set(self.comment_votes.values_list('comment_id', flat=True))

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

    def __str__(self):
        return f'Profile of {self.user.username}'