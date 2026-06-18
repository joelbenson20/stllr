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

# TODO: Decide on allowed tags
# TODO: Remove 'humanize' library

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

def _link_mentions(html, mention_map):
    def replace(match):
        handle = match.group(1)
        url = mention_map.get(handle)
        if url:
            return f'<a href="{url}">@{handle}</a>'
        return match.group(0)
    return _MENTION_RE.sub(replace, html)

# TODO: Mention links should depend on the mention still being valid (If the user/crew is deleted then the mention is deleted by cascade. This is desireable behavior, because then the link will break, as it should.)
def _mention_map_from_content(content):
    from django.contrib.auth import get_user_model
    from crews.models import Crew
    handles = set(_MENTION_RE.findall(content))
    if not handles:
        return {}
    User = get_user_model()
    mention_map = {}
    for u in User.objects.filter(username__in=handles):
        mention_map[u.username] = reverse('users:profile', args=[u.username])
    for c in Crew.objects.filter(handle__in=handles):
        mention_map[c.handle] = reverse('crews:crew_detail', args=[c.handle])
    return mention_map


def _mention_map_from_post(post):
    mention_map = {}
    for m in post.mentions.all():
        if m.user_id:
            mention_map[m.user.username] = reverse('users:profile', args=[m.user.username])
        else:
            mention_map[m.crew.handle] = reverse('crews:crew_detail', args=[m.crew.handle])
    return mention_map


def render_content(content):
    html = markdown_deux.markdown(content)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=_allow_safe_urls, strip=True)
    return mark_safe(_link_mentions(clean, _mention_map_from_content(content)))


@register.filter(name='render_post')
def render_post(post):
    html = markdown_deux.markdown(post.content)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=_allow_safe_urls, strip=True)
    return mark_safe(_link_mentions(clean, _mention_map_from_post(post)))

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
