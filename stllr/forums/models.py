import numpy as np
from django.db import models
from django.conf import settings
from django.db import models
from django.db.models import Case, When, IntegerField
from pages.models import Page


class Post(models.Model):

    class FirmamentQuerySet(models.QuerySet):
        def firmament(self):
            if not self:
                return self.none()
            posts = self.values('id', 'brightness')
            total_posts = posts.count()
            ids = [post['id'] for post in posts]
            brightnesses = np.maximum(np.array([post['brightness'] for post in posts]), 1e-10)
            probabilities = brightnesses / brightnesses.sum()
            chosen_ids = np.random.choice(ids, size=total_posts, p=probabilities, replace=False)
            chosen_order = Case(
                *[When(id=id, then=pos) for pos, id in enumerate(chosen_ids)],
                output_field=IntegerField()
            )
            firmament = Post.objects.filter(id__in=chosen_ids).order_by(chosen_order)
            return firmament
    
    objects = models.Manager()
    firmament = FirmamentQuerySet.as_manager()

    user = models.ForeignKey(
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

    users_star = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PostStar',
        related_name='posts_starred',
        blank=True
    )
    total_stars = models.PositiveIntegerField(default=0)
    brightness = models.FloatField(default=0)

    class Meta:
        default_manager_name = 'firmament'
        indexes = [
            models.Index(fields=['-brightness'])
        ]
        ordering = ['-brightness', '?']

    def __str__(self):
        return f'{self.user}: {self.content}'
    
    
class PostStar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='post_stars', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='stars', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')