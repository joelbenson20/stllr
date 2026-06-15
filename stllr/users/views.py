from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import ContactRelation, Mute


def _profile_base_context(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    contact = None
    if request.user.is_authenticated and request.user != user:
        contact = ContactRelation.objects.filter( #TODO: Make helper function to 'get ContactRelation' status of any two users
            from_user=request.user, to_user=user
        ).first() or ContactRelation.objects.filter(
            from_user=user, to_user=request.user
        ).first()
    return user, {'profile': user.profile, 'contact': contact}


def profile_posts(request, username): #TODO: Posts need to display the page they're under to make contextual sense
    user, context = _profile_base_context(request, username)
    context['posts'] = user.posts.filter(removed=False).select_related('page', 'page__domain').order_by('-created')
    context['active_tab'] = 'posts'
    return render(request, 'profile/detail.html', context)


def profile_stars(request, username):
    user, context = _profile_base_context(request, username)
    context['active_tab'] = 'stars'
    return render(request, 'profile/detail.html', context)

@login_required
def edit(request, username):
    if request.user.username != username:
        return redirect('users:profile', username=username)
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Account updated successfully')
            return redirect('users:profile', request.user.username)
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'profile/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def send_request(request, username):
    to_user = get_object_or_404(get_user_model(), username=username)
    if to_user != request.user:
        ContactRelation.objects.create(from_user=request.user, to_user=to_user)
    return redirect('users:profile', username=username)


@login_required
def accept_request(request, username):
    from_user = get_object_or_404(get_user_model(), username=username)
    contact = get_object_or_404(
        ContactRelation, from_user=from_user, to_user=request.user,
        status=ContactRelation.Status.PENDING
    )
    contact.status = ContactRelation.Status.ACCEPTED
    contact.save()
    return redirect('users:profile', username=username)


@login_required
def decline_request(request, username):
    other_user = get_object_or_404(get_user_model(), username=username)
    ContactRelation.objects.filter(from_user=request.user, to_user=other_user).delete()
    ContactRelation.objects.filter(from_user=other_user, to_user=request.user).delete()
    return redirect('users:profile', username=request.user.username)


@login_required
def remove_contact(request, username):
    other_user = get_object_or_404(get_user_model(), username=username)
    ContactRelation.objects.filter(from_user=request.user, to_user=other_user).delete()
    ContactRelation.objects.filter(from_user=other_user, to_user=request.user).delete()
    return redirect('users:profile', username=username)


@login_required
@require_POST
def mute_user(request, username):
    target = get_object_or_404(get_user_model(), username=username)
    if target == request.user:
        return JsonResponse({'status': 400}, status=400)
    action = request.POST.get('action')
    if action == 'mute':
        Mute.objects.get_or_create(muter=request.user, muted=target)
    elif action == 'unmute':
        Mute.objects.filter(muter=request.user, muted=target).delete()
    else:
        return JsonResponse({'status': 400}, status=400)
    return JsonResponse({'status': 200}, status=200)


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password1'])
            new_user.save()
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})
