from django import template
from django.db.models import Count

register = template.Library()

@register.inclusion_tag('comments/comment_tree.html', takes_context=True)
def render_comment_tree(context, page=None, comments=None):
    if (comments):
        comments = comments.order_by('-total_stars')
        return {
            'comments': comments,
            'user': context.get('user'),
            'request': context.get('request')
        }
    elif page:
        # Get thread level 0 of page comments to "plant" tree
        layer_0 = page.comments.filter(thread_level=0).order_by('-total_stars')
        return {
            'comments': layer_0,
            'user': context.get('user'),
            'request': context.get('request')
        }