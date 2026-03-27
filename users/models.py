from django.contrib.auth.models import AbstractUser
from django.urls import reverse

# Create your models here.
class User(AbstractUser):
    pass

    def get_absolute_url(self):
        return reverse('user', kwargs={'username': self.username})