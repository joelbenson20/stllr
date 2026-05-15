from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from .models import Contact

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
    contact = None
    if request.user.is_authenticated and request.user != user:
        contact = Contact.objects.filter(
            from_user=request.user, to_user=user
        ).first() or Contact.objects.filter(
            from_user=user, to_user=request.user
        ).first()
    return render(
        request,
        'user/profile.html',
        {
            'profile': user.profile,
            'contact': contact
        }
    )

@login_required
def edit(request, username):
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
        'user/edit.html',
        {
            'profile_form': profile_form
        }
    )

@login_required
def comms(request):
    pending_requests = Contact.objects.filter(
        to_user=request.user,
        status=Contact.Status.PENDING
    ).select_related('from_user__profile')
    return render(request, 'user/comms.html', {'pending_requests': pending_requests})


@login_required
def send_request(request, username):
    to_user = get_object_or_404(get_user_model(), username=username)
    if to_user != request.user:
         Contact.objects.create(from_user=request.user, to_user=to_user)
    return redirect('profile', username=username)

@login_required
def accept_request(request, username):
    from_user = get_object_or_404(get_user_model(), username=username)
    contact = get_object_or_404(Contact, from_user=from_user, to_user=request.user, status=Contact.Status.PENDING)
    contact.status = Contact.Status.ACCEPTED
    contact.save()
    return redirect('profile', username=username)

@login_required
def remove_contact(request, username):
    other_user = get_object_or_404(get_user_model(), username=username)
    Contact.objects.filter(
        from_user=request.user, to_user=other_user
    ).delete()
    Contact.objects.filter(
        from_user=other_user, to_user=request.user
    ).delete()
    return redirect('profile', username=username)