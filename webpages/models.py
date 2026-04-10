from django.db import models
from urllib.parse import urlparse
from django.urls import reverse
from django_comments_xtd.moderation import moderator, XtdCommentModerator

# Create your models here.
class Webpage(models.Model):

    canonical = models.CharField(max_length=250, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=400, null=True, blank=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    site_name = models.CharField(max_length=100, null=True, blank=True)
    fav_icon_url = models.URLField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.canonical
    
    def get_absolute_url(self):
        return reverse('webpages:detail', kwargs={'pk': self.pk})
    
    @property
    def hostname(self):
        return urlparse('https://' + self.canonical).hostname
    
    @property
    def link(self):
        return 'https://' + self.canonical
    
    @property
    def num_votes(self):
        return self.votes.count()
    
class WebpageCommentModerator(XtdCommentModerator):
    removal_suggestion_notification = True

moderator.register(Webpage, WebpageCommentModerator)