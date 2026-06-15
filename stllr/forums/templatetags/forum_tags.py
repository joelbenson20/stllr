import re
import random
import bleach
import markdown_deux
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils import timezone

register = template.Library()

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'code', 'pre', 'blockquote',
    'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'a',
    'img',
]
ALLOWED_ATTRS = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
}

def _allow_safe_urls(tag, name, value):
    if name == 'href':
        return value.startswith(('https://', 'http://', '/', '#', 'mailto:'))
    if name == 'src':
        return value.startswith('/')  # only allow self-hosted (relative) URLs
    return True

_MENTION_RE = re.compile(r'@(\w+)')

def _link_mentions(html):
    def replace(match):
        username = match.group(1)
        url = reverse('users:profile', args=[username])
        return f'<a href="{url}">@{username}</a>'
    return _MENTION_RE.sub(replace, html)

@register.filter(name='time_since')
def time_since(value):
    now = timezone.now()
    seconds = int((now - value).total_seconds())
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''} ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    if days < 30:
        return f"{days} day{'s' if days != 1 else ''} ago"
    months = days // 30
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"


@register.simple_tag
def random_seed():
    return random.random()


@register.filter(name='safe_markdown')
def safe_markdown(content):
    html = markdown_deux.markdown(content)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=_allow_safe_urls, strip=True)
    return mark_safe(clean)


@register.simple_tag(takes_context=True)
def ancestry_chain(context, ancestors, post):
    """Render a nested ancestry chain: each ancestor embeds the next via display_children."""
    request = context.get('request')
    flat = context.flatten()

    def render_node(p, inner=''):
        ctx = {**flat, 'post': p, 'display_children': mark_safe(inner)}
        return render_to_string('post/card.html', ctx, request=request)

    html = render_node(post)
    for ancestor in reversed(ancestors):
        html = render_node(ancestor, inner=html)
    return mark_safe(html)


@register.filter(name='render_post')
def render_post(content):
    html = markdown_deux.markdown(content)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=_allow_safe_urls, strip=True)
    return mark_safe(_link_mentions(clean))