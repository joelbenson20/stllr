from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db import models
from webpages.models import Webpage

class User(AbstractUser):

    def get_full_name(self):
        return self.username
    
    def get_absolute_url(self):
        return reverse('user', kwargs={'username': self.username})
    
    @property
    def voted_webpages_ids(self):
        return set(self.webpage_votes.values_list('webpage_id', flat=True))

    
class Vote(models.Model):

    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
    
class WebpageVote(Vote):

    user = models.ForeignKey(User, related_name='webpage_votes', on_delete=models.CASCADE)
    webpage = models.ForeignKey(Webpage, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} : {self.webpage}"
    
    class Meta:
        unique_together = ('user', 'webpage')