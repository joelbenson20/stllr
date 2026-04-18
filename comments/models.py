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

    def __str__(self):
        return f'{self.user}: {self.content}'