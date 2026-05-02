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