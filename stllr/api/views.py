from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from forums.templatetags.utility_tags import safe_markdown_filter
from django.template.loader import render_to_string
from pages.models import Page, PageStar
from forums.models import Post, PostStar
from forums.forms import PostForm
from rooms.consumers import _get_users
from users.models import Action


@login_required
@require_POST
def markdownify(request):
    content = request.POST.get('content', '')
    response = {
        'status': '200',
        'markdown': safe_markdown_filter(content),
    }
    return JsonResponse(response)

@login_required
@require_POST
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def create_post(request):
    new_post = None
    form = PostForm(data=request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        new_post = form.save(commit=False)
        new_post.user = request.user
        if (new_post.parent):
            new_post.thread_level = new_post.parent.thread_level + 1
        new_post.save()
        if (new_post.parent):
            Action.objects.create(
                user=request.user, verb=Action.Verb.REPLIED, object=new_post
            )
        else:
            Action.objects.create(
                user=request.user, verb=Action.Verb.POSTED, object=new_post
            )
        response = {
            'status': '201',
            'postId': new_post.id,
            'post': render_to_string('post/tree.html', {'posts': [new_post]}, request=request)
        }
        return (JsonResponse(response))
    return JsonResponse({'status': '400'})

@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def star_page(request):
    page_id = request.POST.get('id')
    action = request.POST.get('action')
    if page_id and action:
        try:
            page = Page.objects.get(id=page_id)
            if action == 'star':
                PageStar.objects.get_or_create(page=page, user=request.user)
                Action.objects.create(
                    user=request.user, verb=Action.Verb.STARRED, object=page
                )
            else:
                PageStar.objects.filter(page=page, user=request.user).first().delete()
            return JsonResponse({'status': '200'})
        except Page.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})

@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def star_post(request):
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        try:
            post = Post.objects.get(id=post_id)
            if action == 'star':
                PostStar.objects.get_or_create(post=post, user=request.user)
            else:
                PostStar.objects.filter(post=post, user=request.user).first().delete()
            return JsonResponse({'status': '200'})
        except Post.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})

def get_room_count(request):
    ids = [i.strip() for i in request.GET.get('ids', '').split(',') if i.strip()]
    counts = {page_id: len(_get_users(f'room_{page_id}')) for page_id in ids}
    return JsonResponse(counts)