from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django.middleware.csrf import get_token
from forums.templatetags.safe_markdown import safe_markdown_filter
from django.template.loader import render_to_string
from django.core.cache import cache
from pages.models import Page
from forums.models import Comment
from forums.forms import CommentForm
from rooms.consumers import _get_users
import secrets

@login_required
def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

@login_required
def ws_ticket(request):
    token = secrets.token_urlsafe(32)
    cache.set(f'ws_ticket:{token}', request.user.id, timeout=30)
    return JsonResponse({'ticket': token})

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
def create_comment(request):
    new_comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        new_comment = form.save(commit=False)
        new_comment.user = request.user
        if (new_comment.parent):
            new_comment.thread_level = new_comment.parent.thread_level + 1
        new_comment.save()
        response = {
            'status': '201',
            'commentId': new_comment.id,
            'comment': render_to_string('comments/tree.html', {'comments': [new_comment]}, request=request)
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
                page.users_star.add(request.user)
            else:
                page.users_star.remove(request.user)
            return JsonResponse({'status': '200'})
        except Page.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})

@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def star_comment(request):
    comment_id = request.POST.get('id')
    action = request.POST.get('action')
    if comment_id and action:
        try:
            comment = Comment.objects.get(id=comment_id)
            if action == 'star':
                comment.users_star.add(request.user)
            else:
                comment.users_star.remove(request.user)
            return JsonResponse({'status': '200'})
        except Comment.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})

@login_required
def get_room_count(request):
    ids = [i.strip() for i in request.GET.get('ids', '').split(',') if i.strip()]
    counts = {page_id: len(_get_users(f'room_{page_id}')) for page_id in ids}
    return JsonResponse(counts)