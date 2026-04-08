from copy import copy

from django import template


register = template.Library()


def _like_count(node):
    return len(node.get('likedit_users', []))


def _sort_comment_tree(nodes):
    sorted_nodes = []

    for node in nodes:
        node_copy = copy(node)
        node_copy['children'] = _sort_comment_tree(node.get('children', []))
        sorted_nodes.append(node_copy)

    return sorted(
        sorted_nodes,
        key=lambda node: (-_like_count(node), node['comment'].order),
    )


@register.simple_tag
def sort_xtdcomment_tree(comments):
    if not comments:
        return []
    return _sort_comment_tree(list(comments))