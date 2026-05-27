import numpy as np
from django.db import models
from urllib.parse import urlparse
from django.urls import reverse
from django.utils.http import urlencode
from taggit.managers import TaggableManager
from django.conf import settings
from django.db import models
from django.db.models import Case, When, IntegerField
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.fields import ArrayField


class Page(models.Model):
    class FirmamentQuerySet(models.QuerySet):
        def firmament(self):
            if not self:
                return self.none()
            pages = self.values('id', 'brightness')
            total_pages = pages.count()
            ids = [page['id'] for page in pages]
            brightnesses = np.maximum(np.array([page['brightness'] for page in pages]), 1e-10)
            probabilities = brightnesses / brightnesses.sum()
            chosen_ids = np.random.choice(ids, size=total_pages, p=probabilities, replace=False)
            chosen_order = Case(
                *[When(id=id, then=pos) for pos, id in enumerate(chosen_ids)],
                output_field=IntegerField()
            )
            firmament = Page.objects.filter(id__in=chosen_ids).order_by(chosen_order)
            return firmament
        
    class Protocol(models.TextChoices):
        HTTP = 'http', 'http://'
        HTTPS = 'https', 'https://'
        
    objects = models.Manager()
    firmament = FirmamentQuerySet.as_manager()

    canonical = models.CharField(max_length=250, unique=True)
    supported_protocols = ArrayField(models.CharField(max_length=10), default=list, blank=True)
    title = models.CharField(max_length=500)
    tags = TaggableManager(blank=True)
    description = models.TextField(max_length=500, blank=True)
    image_url = models.URLField(max_length=250, blank=True)
    image = models.ImageField(max_length=255, upload_to='images/pages', blank=True)
    domain = models.ForeignKey('Domain', related_name='pages', on_delete=models.CASCADE)
    
    content = models.TextField(blank=True)
    search_vector = SearchVectorField(null=True, editable=False)

    users_star = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PageStar',
        related_name='pages_starred',
        blank=True
    )
    # Done by Claude, requires review
    users_bookmark = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PageBookmark',
        related_name='pages_bookmarked',
        blank=True
    )
    total_stars = models.PositiveIntegerField(default=0, editable=False)
    brightness = models.FloatField(default=0, editable=False)
    brightness_index = models.PositiveIntegerField(editable=False)
    rise = models.IntegerField(default=0, editable=False)

    is_active = models.BooleanField(default=True)

    actions = GenericRelation('users.Action', content_type_field='object_ct', object_id_field='object_id')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.brightness_index = Page.objects.count() + 1
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['-brightness']),
            GinIndex(fields=['search_vector'], name='page_search_vector_gin'),
        ]
        ordering = ['-brightness', '?']
    
    def __str__(self):
        return self.canonical
    
    @property
    def link(self):
        if self.Protocol.HTTPS in self.supported_protocols:
            return self.Protocol.HTTPS + '://' + self.canonical
        if self.Protocol.HTTP in self.supported_protocols:
            return self.Protocol.HTTP + '://' + self.canonical
        return self.Protocol.HTTPS + '://' + self.canonical
    
    
class PageStar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='page_stars', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='stars', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'page')

class PageBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='page_bookmarks', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='bookmarks', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'page')


class Domain(models.Model):

    CATEGORIES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('television', 'TV'),
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
    fav_icon_bg_light = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.site_name or self.name
