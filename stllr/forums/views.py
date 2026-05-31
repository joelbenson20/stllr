from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.template.loader import render_to_string
from django_ratelimit.decorators import ratelimit
from pages.models import Page
from .models import Post, PostStar
from .forms import PostForm
from .templatetags.utility_tags import safe_markdown_filter
from users.models import Action


def forum(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    posts_qs = Post.firmament.filter(page=page, thread_level=0)
    posts = posts_qs.firmament() if posts_qs else posts_qs.none()
    return render(request, 'forum.html', context={'page': page, 'posts': posts})


@login_required
@require_POST
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def create_post(request):
    form = PostForm(data=request.POST)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        if new_post.parent:
            new_post.thread_level = new_post.parent.thread_level + 1
        new_post.save()
        verb = Action.Verb.REPLIED if new_post.parent else Action.Verb.POSTED
        Action.objects.create(actor=request.user, verb=verb, object=new_post)
        return JsonResponse({
            'status': '201',
            'postId': new_post.id,
            'post': render_to_string('post/tree.html', {'posts': [new_post]}, request=request),
        })
    return JsonResponse({'status': '400'})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    ancestors = []
    node = post.parent
    while node:
        ancestors.insert(0, node)
        node = node.parent
    return render(request, 'post/detail.html', {'post': post, 'ancestors': ancestors})


@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def toggle_star(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    action = request.POST.get('action')
    if action == 'star':
        PostStar.objects.get_or_create(post=post, user=request.user)
    elif action == 'unstar':
        star = PostStar.objects.filter(post=post, user=request.user).first()
        if star:
            star.delete()
    else:
        return JsonResponse({'status': '400'}, status=400)
    return JsonResponse({'status': '200'})


@login_required
def remove_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author and not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        post.removed = True
        post.removed_by = 'author' if request.user == post.author else 'moderator'
        post.save(update_fields=['removed', 'removed_by'])
        return redirect('forums:remove_post_success')
    return render(request, 'post/remove_confirm.html', {'post': post})


def remove_post_success(request):
    return render(request, 'post/remove_success.html')


@login_required
@require_POST
def markdownify(request):
    content = request.POST.get('content', '')
    return JsonResponse({'status': '200', 'markdown': safe_markdown_filter(content)})
