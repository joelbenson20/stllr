from django import template
from crews.models import Membership

register = template.Library()


@register.simple_tag
def get_membership(crew, user):
    if not user or not getattr(user, 'is_authenticated', False):
        return None
    return Membership.objects.filter(crew=crew, user=user).first()
