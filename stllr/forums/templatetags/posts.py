from django import template

register = template.Library()

@register.inclusion_tag('posts/tree.html', takes_context=True)
def render_post_tree(context, page=None, posts=None):
    if (posts):
        return {
            'posts': posts,
            'user': context.get('user'),
            'request': context.get('request')
        }
    elif page:
        # Get thread level 0 of page posts to "plant" tree
        layer_0 = page.posts.filter(thread_level=0).firmament()
        return {
            'posts': layer_0,
            'user': context.get('user'),
            'request': context.get('request')
        }