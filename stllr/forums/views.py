import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from django.db.models.expressions import RawSQL
from django_ratelimit.decorators import ratelimit
from pages.models import Page
from .models import Post
from .forms import PostForm
from .templatetags.forum_tags import render_post


def forum(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    return render(request, 'forum.html', {'page': page})


def feed(request):
    page = get_object_or_404(Page, pk=request.GET.get('page_id'))
    seed = float(request.GET.get('seed', random.random()))
    parent_id = request.GET.get('parent_id')

    with connection.cursor() as cursor:
        cursor.execute('SELECT setseed(%s)', [seed])

    if parent_id:
        posts = Post.objects.filter(parent_id=parent_id)
    else:
        posts = Post.objects.filter(page=page, thread_level=0)

    posts = posts.order_by(RawSQL('brightness * RANDOM()', []).desc())

    paginator = Paginator(posts, 10)
    try:
        posts = paginator.page(request.GET.get('p', 1))
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        return HttpResponse('')

    return render(request, 'post/list.html', {'posts': posts})


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
            required_mention = f'@{new_post.parent.author.username}'
            after = new_post.content[len(required_mention):]
            if (not new_post.content.startswith(required_mention)
                    or not after or not after[0].isspace()
                    or not after.strip()):
                return JsonResponse(
                    {'status': 400, 'errors': {'content': [f'Reply must start with {required_mention}.']}},
                    status=400
                )
        new_post.save()
        return JsonResponse({
            'status': 201,
            'postId': new_post.id,
            'post': render_to_string('post/tree.html', {'posts': [new_post]}, request=request),
        }, status=201)
    return JsonResponse({'status': 400, 'errors': form.errors}, status=400)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    ancestors = []
    node = post.parent
    while node:
        ancestors.insert(0, node)
        node = node.parent
    return render(request, 'post/detail.html', {'post': post, 'ancestors': ancestors})



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
    return JsonResponse({'status': 200, 'markdown': render_post(content)}, status=200)
