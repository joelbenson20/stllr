from django.db import models
from urllib.parse import urlparse
from django.urls import reverse
from django_comments_xtd.moderation import moderator, XtdCommentModerator
from django.utils.http import urlencode
from taggit.managers import TaggableManager

# Create your models here.
class Page(models.Model):

    canonical = models.CharField(max_length=250, unique=True)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=30)
    tags = TaggableManager(blank=True)
    description = models.TextField(max_length=400, blank=True)
    image_url = models.URLField(max_length=250, blank=True)
    site_name = models.CharField(max_length=100, blank=True)
    fav_icon_url = models.URLField(max_length=250, blank=True)

    html = models.TextField(blank=True)

    def __str__(self):
        return self.canonical
    
    def get_absolute_url(self):
        query_params = {'p': self.canonical}
        return f"{reverse('forum:page_detail')}?{urlencode(query_params)}"
    
    @property
    def hostname(self):
        return urlparse('https://' + self.canonical).hostname
    
    @property
    def link(self):
        return 'https://' + self.canonical
    
    @property
    def num_votes(self):
        return self.votes.count()
    
class PageCommentModerator(XtdCommentModerator):
    removal_suggestion_notification = True

moderator.register(Page, PageCommentModerator)