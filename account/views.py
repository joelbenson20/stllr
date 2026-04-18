from django.shortcuts import get_object_or_404, render
from .models import User, Profile
from .forms import UserRegistrationForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
            messages.success(
                request,
                'Profile updated successfully'
            )
        else:
            messages.error(request, 'Error updating your profile')
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

    context = {
        'user': user,
        'voted_pages': user.voted_pages,
    }
    
    return render(request, 'user.html', context)