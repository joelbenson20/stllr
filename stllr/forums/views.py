from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from pages.models import Page
from .models import Post

# Done by Claude, requires review
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'post/detail.html', {'post': post})

def forum(request):
    canonical = request.GET.get('p')
    page = get_object_or_404(Page, canonical=canonical)
    return render(request, 'forum.html', context={'page': page})

# Done by Claude, requires review
@login_required
def remove_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.user and not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        # Done by Claude, requires review
        post.removed = True
        post.removed_by = 'author' if request.user == post.user else 'moderator'
        post.save(update_fields=['removed', 'removed_by'])
        return redirect('forums:remove_post_success')
    return render(request, 'post/remove_confirm.html', {'post': post})

# Done by Claude, requires review
def remove_post_success(request):
    return render(request, 'post/remove_success.html')