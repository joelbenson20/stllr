from django.db import models
from django.conf import settings
from pages.models import Page


class Comment(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE
    )
    page = models.ForeignKey(
        Page,
        related_name='comments',
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'Comment',
        related_name='children',
        on_delete=models.CASCADE,
        null=True
    )
    thread_level = models.IntegerField(default=0)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    users_star = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CommentStar',
        related_name='comments_starred',
        blank=True
    )
    total_stars = models.PositiveIntegerField(default=0)
    brightness = models.FloatField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['-brightness'])
        ]
        ordering = ['-brightness', '?']

    def __str__(self):
        return f'{self.user}: {self.content}'
    
    
class CommentStar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comment_stars', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='stars', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')