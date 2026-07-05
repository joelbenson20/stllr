from django import template
from django.contrib.contenttypes.models import ContentType
from stars.models import Star

register = template.Library()


@register.filter
def starred_by(obj, user):
    if not user.is_authenticated:
        return False
    ct = ContentType.objects.get_for_model(obj)
    return Star.objects.filter(user=user, object_ct=ct, object_id=obj.pk).exists()


@register.filter
def object_ct_name(obj):
    return obj.__class__.__name__.lower()
