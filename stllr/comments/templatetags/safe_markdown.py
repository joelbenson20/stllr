import bleach
import markdown_deux
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'code', 'pre', 'blockquote',
    'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'a',
]
ALLOWED_ATTRS = {
    'a': ['href', 'title']
}

def _allow_safe_urls(tag, name, value):
    if name == 'href':
        return value.startswith(('https://', 'http://', '/', '#', 'mailto:'))
    return True

@register.filter(name='safe_markdown')
def safe_markdown_filter(content):
    html = markdown_deux.markdown(content)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=_allow_safe_urls, strip=True)
    return mark_safe(clean)