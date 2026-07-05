import random
from django import template

register = template.Library()

@register.simple_tag
def random_seed():
    return random.random()

@register.filter
def pinned_by(page, user):
    if not user or not user.is_authenticated:
        return False
    return page.pins.filter(user=user).exists()
