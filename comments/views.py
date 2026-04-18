from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import CommentForm
from django.http import JsonResponse
from pages.models import Page

@login_required
@require_POST
def post_comment(request, page_id):
    page = get_object_or_404(
        Page,
        id=page_id,
    )
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        print('Form cleaned data:', cd)
        comment = form.save(commit=False)
        comment.user = request.user
        comment.page = page
        if (comment.parent):
            comment.thread_level = comment.parent.thread_level + 1
        comment.save()
        return (JsonResponse({'status': '201'}))
    print('Form errors:', form.errors)
    print(request.POST)
    return JsonResponse({'status': '400'})