from django.db import models, connection
from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from pages.models import Page
from crews.models import Crew


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
    removed = models.BooleanField(default=False) #TODO: How do reply mentions work with removing posts and hiding the author? Also, forced mention changes the dynamic of a reply a bit. Worth thinking about.
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

    @property
    def descendant_count(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE tree AS (
                    SELECT id FROM forums_post WHERE parent_id = %s
                    UNION ALL
                    SELECT p.id FROM forums_post p INNER JOIN tree t ON p.parent_id = t.id
                )
                SELECT COUNT(*) FROM tree
            """, [self.pk])
            return cursor.fetchone()[0]

    def __str__(self):
        return f'{self.author}: {self.content}'


class Mention(models.Model):

    post = models.ForeignKey(
        Post,
        related_name='mentions',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='mentions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    crew = models.ForeignKey(
        Crew,
        related_name='mentions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, crew__isnull=True) |
                    models.Q(user__isnull=True, crew__isnull=False)
                ),
                name='mention_exactly_one_target'
            ),
            models.UniqueConstraint(fields=['post', 'user'], name='unique_mention_user', condition=models.Q(user__isnull=False)),
            models.UniqueConstraint(fields=['post', 'crew'], name='unique_mention_crew', condition=models.Q(crew__isnull=False)),
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['crew']),
        ]

    def __str__(self):
        target = f'@{self.user.username}' if self.user_id else f'@{self.crew.handle}'
        return f'{target} in post {self.post_id}'


