import random
from django import template

register = template.Library()

@register.simple_tag
def random_seed():
    return random.random()
