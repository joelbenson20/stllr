import numpy as np
from django.db import models
from django.conf import settings
from django.db.models import Case, When, IntegerField
from django.db.models.expressions import RawSQL
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
    users_pin = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PagePin',
        related_name='pages_pinned',
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

    def get_similar_pages(self, limit=10):
        if not self.search_vector:
            return Page.objects.none()
        # Fetch only lexemes that are safe tsquery atoms — URL fragments and
        # punctuation from scraped content would otherwise cause a syntax error.
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT lexeme FROM unnest((SELECT search_vector FROM pages_page WHERE id = %s)) "
                "WHERE lexeme ~ '^[a-zA-Z][a-zA-Z0-9]*$'",
                [self.pk]
            )
            lexemes = [row[0] for row in cursor.fetchall()]
        if not lexemes:
            return Page.objects.none()
        return (
            Page.objects
            .filter(is_active=True)
            .exclude(pk=self.pk)
            .annotate(
                score=RawSQL(
                    "ts_rank(search_vector, to_tsquery('english', %s)) * brightness",
                    [' | '.join(lexemes)]
                )
            )
            .filter(score__gt=0)
            .order_by('-score')[:limit]
        )
    
    
class PageStar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='page_stars', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='stars', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'page')

class PagePin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='page_pins', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, related_name='pins', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'page')


class Domain(models.Model):

    CATEGORIES = [
        ('article', 'Article'),
        ('news', 'News'),
        ('video', 'Video'),
        ('television', 'TV'),
        ('music', 'Music'),
        ('social', 'Social'),
        ('shopping', 'Shopping'),
        ('reference', 'Reference'),
        ('app', 'App'),
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
