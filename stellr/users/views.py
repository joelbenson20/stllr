from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password1']
            )
            new_user.save()
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

def profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    return render(
        request,
        'account/profile.html',
        { 'profile': user.profile})

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
            return redirect('profile', request.user.username)
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