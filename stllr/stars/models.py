from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Star(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='stars', on_delete=models.CASCADE)
    object_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('object_ct', 'object_id')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'object_ct', 'object_id'], name='unique_star_per_user_object'),
        ]
        indexes = [
            models.Index(fields=['object_ct', 'object_id']),
        ]
