from django import template
from pages.models import Page

register = template.Library()

@register.inclusion_tag('comments/comment_tree.html')
def render_comment_tree(page=None, comments=None):
    if (comments):
        return {
            'comments': comments
        }
    elif page:
        layer_0 = page.comments.filter(thread_level=0)
        return {
            'comments': layer_0
            }