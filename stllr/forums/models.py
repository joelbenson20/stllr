from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from pages.models import Page


class Post(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='posts',
        on_delete=models.CASCADE
    )
    page = models.ForeignKey(
        Page,
        related_name='posts',
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'Post',
        related_name='children',
        on_delete=models.CASCADE,
        null=True
    )
    thread_level = models.IntegerField(default=0)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    stars = GenericRelation('stars.Star', content_type_field='object_ct', object_id_field='object_id')
    total_stars = models.PositiveIntegerField(default=0)
    brightness = models.FloatField(default=0)
    removed = models.BooleanField(default=False)
    removed_by = models.CharField(
        max_length=16,
        choices=[('author', 'the author'), ('moderator', 'a moderator')],
        null=True,
        blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['-brightness'])
        ]
        ordering = ['-brightness', '?']

    def get_absolute_url(self):
        return reverse('forums:post_detail', args=[self.pk])

    def get_descendants(self):
        ids = []
        frontier = list(self.children.values_list('id', flat=True))
        while frontier:
            ids.extend(frontier)
            frontier = list(Post.objects.filter(parent_id__in=frontier).values_list('id', flat=True))
        return Post.objects.filter(id__in=ids)

    @property
    def descendant_count(self):
        return self.get_descendants().count()

    def __str__(self):
        return f'{self.author}: {self.content}'
    
    
