from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import ContactRelation, Action, Mute


@login_required
def search_users(request):
    User = get_user_model()
    q = request.GET.get('q', '').strip()
    users = []
    if q:
        users = list(
            User.objects.filter(username__icontains=q)
            .exclude(id=request.user.id)
            .select_related('profile')[:10]
        )
    html = render_to_string('user/search_results.html', {'users': users}, request=request)
    return JsonResponse({'html': html})


@login_required
def remove_action(request, action_id):
    action = get_object_or_404(Action, id=action_id, actor=request.user)
    action.removed = True
    action.save(update_fields=['removed'])
    messages.success(request, "Removed from your activity feed.")
    return redirect('profile', username=request.user.username)


def profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    contact = None
    if request.user.is_authenticated and request.user != user:
        contact = ContactRelation.objects.filter(
            from_user=request.user, to_user=user
        ).first() or ContactRelation.objects.filter(
            from_user=user, to_user=request.user
        ).first()
    return render(
        request,
        'profile/detail.html',
        {
            'profile': user.profile,
            'contact': contact,
            'actions': user.actions.filter(removed=False),
        }
    )

@login_required
def edit(request, username):
    if request.user.username != username:
        return redirect('profile', username=username)
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Account updated successfully')
            return redirect('profile', request.user.username)
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
    return redirect('profile', username=username)


@login_required
def accept_request(request, username):
    from_user = get_object_or_404(get_user_model(), username=username)
    contact = get_object_or_404(
        ContactRelation, from_user=from_user, to_user=request.user,
        status=ContactRelation.Status.PENDING
    )
    contact.status = ContactRelation.Status.ACCEPTED
    contact.save()
    return redirect('profile', username=username)


@login_required
def decline_request(request, username):
    other_user = get_object_or_404(get_user_model(), username=username)
    ContactRelation.objects.filter(from_user=request.user, to_user=other_user).delete()
    ContactRelation.objects.filter(from_user=other_user, to_user=request.user).delete()
    return redirect('profile', username=request.user.username)


@login_required
def remove_contact(request, username):
    other_user = get_object_or_404(get_user_model(), username=username)
    ContactRelation.objects.filter(from_user=request.user, to_user=other_user).delete()
    ContactRelation.objects.filter(from_user=other_user, to_user=request.user).delete()
    return redirect('profile', username=username)


@login_required
@require_POST
def mute_user(request, username):
    target = get_object_or_404(get_user_model(), username=username)
    if target == request.user:
        return JsonResponse({'status': '400'}, status=400)
    action = request.POST.get('action')
    if action == 'mute':
        Mute.objects.get_or_create(muter=request.user, muted=target)
    elif action == 'unmute':
        Mute.objects.filter(muter=request.user, muted=target).delete()
    else:
        return JsonResponse({'status': '400'}, status=400)
    return JsonResponse({'status': '200'})


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
