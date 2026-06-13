import re
import random
import bleach
import markdown_deux
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

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

@register.simple_tag
def random_seed():
    return random.random()


@register.filter(name='safe_markdown')
def safe_markdown(content):
    html = markdown_deux.markdown(content)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=_allow_safe_urls, strip=True)
    return mark_safe(clean)


@register.filter(name='render_post')
def render_post(content):
    html = markdown_deux.markdown(content)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=_allow_safe_urls, strip=True)
    return mark_safe(_link_mentions(clean))