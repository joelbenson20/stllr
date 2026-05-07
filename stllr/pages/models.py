from django.db import models
from urllib.parse import urlparse
from django.urls import reverse
from django.utils.http import urlencode
from taggit.managers import TaggableManager
from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Page(models.Model):
    canonical = models.CharField(max_length=250, unique=True)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=30, blank=True)
    tags = TaggableManager(blank=True)
    description = models.TextField(max_length=400, blank=True)
    image_url = models.URLField(max_length=250, blank=True)
    image = models.ImageField(max_length=255, upload_to='images/pages', blank=True)
    domain = models.ForeignKey('Domain', related_name='pages', on_delete=models.CASCADE)
    
    inner_text = models.TextField(blank=True)
    search_vector = SearchVectorField(null=True, editable=False)

    users_star = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PageStar',
        related_name='pages_starred',
        blank=True
    )
    total_stars = models.PositiveIntegerField(default=0)
    brightness = models.FloatField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['-brightness']),
            GinIndex(fields=['search_vector'], name='page_search_vector_gin'),
        ]
        ordering = ['-brightness', '?']
    
    def __str__(self):
        return self.canonical
    
    def get_absolute_url(self):
        query_params = {'p': self.canonical}
        return f"{reverse('pages:detail')}?{urlencode(query_params)}"
    
    @property
    def link(self):
        return 'https://' + self.canonical
    
    
class PageStar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='page_stars', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='stars', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'page')


class Domain(models.Model):

    CATEGORIES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('social', 'Social'),
        ('shopping', 'Shopping'),
        ('reference', 'Reference'),
        ('news', 'News'),
    ]

    name = models.CharField(unique=True, max_length=100)
    site_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, blank=True)
    fav_icon_url = models.URLField(max_length=250, blank=True)
    fav_icon = models.ImageField(max_length=255, upload_to='images/domains', blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.site_name or self.name
