from django.contrib.auth.models import AbstractUser
from django.urls import reverse
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

    
class Vote(models.Model):

    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
    
class PageVote(Vote):

    user = models.ForeignKey(User, related_name='page_votes', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} : {self.page}"
    
    class Meta:
        unique_together = ('user', 'page')