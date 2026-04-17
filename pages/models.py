from django.db import models
from urllib.parse import urlparse
from django.urls import reverse
from django.utils.http import urlencode
from taggit.managers import TaggableManager
from django.conf import settings

class Page(models.Model):
    canonical = models.CharField(max_length=250, unique=True)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=30, blank=True)
    tags = TaggableManager(blank=True)
    description = models.TextField(max_length=400, blank=True)
    image_url = models.URLField(max_length=250, blank=True)
    domain = models.ForeignKey('Domain', related_name='pages', on_delete=models.CASCADE)
    inner_text = models.TextField(blank=True)

    _is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.canonical
    
    def get_absolute_url(self):
        query_params = {'p': self.canonical}
        return f"{reverse('pages:detail')}?{urlencode(query_params)}"
    
    @property
    def is_active(self):
        return self._is_active and self.domain.is_active

    @property
    def link(self):
        return 'https://' + self.canonical
    
    @property
    def num_votes(self):
        return self.votes.count()
    
    
class PageVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='page_votes', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='votes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'page')


class Domain(models.Model):
    name = models.CharField(unique=True, max_length=100)
    site_name = models.CharField(max_length=100, blank=True)
    fav_icon_url = models.URLField(max_length=250, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.site_name or self.name
