from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import CommentForm
from django.http import JsonResponse
from .models import Comment
from pages.models import Page
from django.template.loader import render_to_string
from django_ratelimit.decorators import ratelimit

@login_required
@require_POST
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def post_comment(request):
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
            'comment': render_to_string('comments/comment.html', {'comment': new_comment}, request=request)
        }
        return (JsonResponse(response))
    return JsonResponse({'status': '400'})

@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def comment_star(request):
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