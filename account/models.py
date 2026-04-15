from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django.db import models
from forum.models import Page

class User(AbstractUser):

    def get_full_name(self):
        return self.username
    
    def get_absolute_url(self):
        return reverse('user', kwargs={'username': self.username})
    
    @property
    def voted_pages(self):
        return Page.objects.filter(votes__user=self)
    
    @property
    def voted_pages_ids(self):
        return set(self.page_votes.values_list('page_id', flat=True))

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
    
class Vote(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
    
class PageVote(Vote):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='page_votes', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} : {self.page}"
    
    class Meta:
        unique_together = ('user', 'page')