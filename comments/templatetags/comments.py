from django import template
from django.db.models import Count

register = template.Library()

@register.inclusion_tag('comments/comment_tree.html', takes_context=True)
def render_comment_tree(context, page=None, comments=None):
    if (comments):
        # Sort comments by vote count
        comments = (comments
        .annotate(vote_count=Count('votes'))
        .order_by('-vote_count')
        )
        # Render comment trees
        return {
            'comments': comments,
            'user': context.get('user')
        }
    elif page:
        # Get thread level 0 of page comments
        layer_0 = page.comments.filter(thread_level=0)
        # Sort comments by vote count
        layer_0 = (layer_0
        .annotate(vote_count=Count('votes'))
        .order_by('-vote_count')
        )
        return {
            'comments': layer_0,
            'user': context.get('user')
            }