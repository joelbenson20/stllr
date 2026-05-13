from django import template

register = template.Library()

@register.inclusion_tag('comments/comment_tree.html', takes_context=True)
def render_comment_tree(context, page=None, comments=None):
    if (comments):
        return {
            'comments': comments,
            'user': context.get('user'),
            'request': context.get('request')
        }
    elif page:
        # Get thread level 0 of page comments to "plant" tree
        layer_0 = page.comments.filter(thread_level=0).firmament()
        return {
            'comments': layer_0,
            'user': context.get('user'),
            'request': context.get('request')
        }