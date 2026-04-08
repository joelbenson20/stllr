from django.shortcuts import get_object_or_404, render
from users.models import User
from django_comments_xtd.models import XtdComment

# Create your views here.
def user(request, username):

    user = get_object_or_404(User, username=username)


    comments = list(
        XtdComment.objects.filter(user=user, is_public=True)
        .order_by('-submit_date')
        .select_related('content_type', 'user')
    )

    parent_ids = {
        comment.parent_id
        for comment in comments
        if comment.parent_id and comment.parent_id != comment.pk
    }
    parent_comments_by_id = XtdComment.objects.in_bulk(parent_ids)

    for comment in comments:
        if comment.parent_id and comment.parent_id != comment.pk:
            comment.parent_comment = parent_comments_by_id.get(comment.parent_id)
        else:
            comment.parent_comment = None

    context = {
        'user': user,
        'voted_webpages': user.voted_webpages,
        'comments': comments,
    }
    
    return render(request, 'user.html', context)