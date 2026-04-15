from django.shortcuts import get_object_or_404, render
from .models import User, Profile
from django_comments_xtd.models import XtdComment
from .forms import UserRegistrationForm, ProfileEditForm
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password1']
            )
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(
                request,
                'account/register_done.html',
                {'new_user': new_user}
            )
    else:
        user_form = UserRegistrationForm()
    return render(
        request,
        'account/register.html',
        {'user_form': user_form}
    )

@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')

@login_required
def edit(request):
    if request.method == 'POST':
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES
        )
        if profile_form.is_valid():
            profile_form.save()
    else:
        profile_form=ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        'account/edit.html',
        {
            'profile_form': profile_form
        }
    )

def user(request, username):

    user = get_object_or_404(User, username=username)

    comments = list(
        XtdComment.objects.filter(user=user, is_public=True)
        .order_by('-submit_date')
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
        'voted_pages': user.voted_pages,
        'comments': comments,
    }
    
    return render(request, 'user.html', context)