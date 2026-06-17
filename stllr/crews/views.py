from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from .forms import CrewForm
from .models import Crew, Membership

User = get_user_model()


def crews(request):
    return render(request, 'crews.html')


def _crew_base_context(request, handle):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    membership = None
    if request.user.is_authenticated:
        membership = Membership.objects.filter(crew=crew, user=request.user).first()
    return crew, {'crew': crew, 'membership': membership}


def crew_beacons(request, handle):
    _, context = _crew_base_context(request, handle)
    context['active_tab'] = 'beacons'
    return render(request, 'crew/detail.html', context)


def crew_members(request, handle):
    crew, context = _crew_base_context(request, handle)
    context['active_tab'] = 'members'
    context['members'] = (
        Membership.objects
        .filter(crew=crew, status=Membership.Status.ACCEPTED)
        .select_related('user')
        .order_by('joined')
    )
    return render(request, 'crew/detail.html', context)


def crew_mentions(request, handle):
    _, context = _crew_base_context(request, handle)
    context['active_tab'] = 'mentions'
    return render(request, 'crew/detail.html', context)


def crew_stars(request, handle):
    _, context = _crew_base_context(request, handle)
    context['active_tab'] = 'stars'
    return render(request, 'crew/detail.html', context)



@login_required
def create_crew(request):
    if request.method == 'POST':
        form = CrewForm(data=request.POST, files=request.FILES, requesting_user=request.user)
        if form.is_valid():
            crew = form.save(commit=False)
            crew.creator = request.user
            crew.save()
            messages.success(request, f'{crew.name} (@{crew.handle}) created.')
            return redirect(crew.get_absolute_url())
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CrewForm(requesting_user=request.user)
    return render(request, 'crew/form.html', {'form': form})


@login_required
def edit_crew(request, handle):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    if request.user.pk not in crew.admin_pks:
        return redirect(crew.get_absolute_url())
    if request.method == 'POST':
        form = CrewForm(data=request.POST, files=request.FILES, instance=crew, requesting_user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Crew updated.')
            return redirect(crew.get_absolute_url())
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CrewForm(instance=crew, requesting_user=request.user)
    return render(request, 'crew/form.html', {'form': form, 'crew': crew})


@login_required
def invite_members(request, handle):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    requester = Membership.objects.filter(
        crew=crew, user=request.user, status=Membership.Status.ACCEPTED
    ).first()
    if not requester or requester.role == Membership.Role.MEMBER:
        return redirect(crew.get_absolute_url())
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        users = (
            User.objects
            .filter(username__icontains=q)
            .exclude(pk=request.user.pk)
            [:20]
        )
        memberships = {
            m.user_id: m
            for m in Membership.objects.filter(crew=crew, user__in=users)
        }
        results = [{'user': u, 'membership': memberships.get(u.pk)} for u in users]
    return render(request, 'invite_members.html', {'crew': crew, 'q': q, 'results': results})


def find_crews(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        crews = Crew.objects.filter(
            Q(name__icontains=q) | Q(handle__icontains=q) | Q(bio__icontains=q)
        )[:20]
        memberships = {}
        if request.user.is_authenticated:
            for m in Membership.objects.filter(crew__in=crews, user=request.user):
                memberships[m.crew_id] = m
        for crew in crews:
            results.append({'crew': crew, 'membership': memberships.get(crew.pk)})
    return render(request, 'find_crews.html', {'q': q, 'results': results})


@login_required
def send_invite(request, handle, username):
    from comms.models import Notification
    from comms.notifications import notify
    crew = get_object_or_404(Crew, handle__iexact=handle)
    if request.user.pk not in crew.admin_pks:
        return HttpResponseForbidden()
    user = get_object_or_404(User, username=username)
    membership, created = Membership.objects.get_or_create(
        crew=crew, user=user,
        defaults={'status': Membership.Status.INVITED, 'role': Membership.Role.MEMBER},
    )
    if created:
        notify(recipient=user, event=Notification.Event.CREW_INVITE, object=crew, actor=request.user)
    return HttpResponse(status=200)


@login_required
def join_crew(request, handle):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    status = Membership.Status.ACCEPTED if crew.is_open else Membership.Status.REQUESTED
    membership, _ = Membership.objects.get_or_create(
        crew=crew, user=request.user,
        defaults={'status': status, 'role': Membership.Role.MEMBER},
    )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'crew/status_button.html',
            {'crew': crew, 'membership': membership},
            request=request,
        ))
    return redirect(crew.get_absolute_url())


@login_required
def leave_crew(request, handle):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    Membership.objects.filter(crew=crew, user=request.user).exclude(
        role=Membership.Role.OWNER
    ).delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'crew/status_button.html',
            {'crew': crew, 'membership': None},
            request=request,
        ))
    return redirect(crew.get_absolute_url())


@login_required
def accept_invite(request, handle):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    membership = get_object_or_404(
        Membership, crew=crew, user=request.user, status=Membership.Status.INVITED
    )
    membership.status = Membership.Status.ACCEPTED
    membership.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'crew/status_button.html',
            {'crew': crew, 'membership': membership},
            request=request,
        ))
    return redirect(crew.get_absolute_url())


@login_required
def decline_invite(request, handle):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    Membership.objects.filter(
        crew=crew, user=request.user, status=Membership.Status.INVITED
    ).delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'crew/status_button.html',
            {'crew': crew, 'membership': None},
            request=request,
        ))
    return redirect(crew.get_absolute_url())


@login_required
def remove_member(request, handle, username):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    requester = Membership.objects.filter(
        crew=crew, user=request.user, status=Membership.Status.ACCEPTED
    ).first()
    if not requester or requester.role == Membership.Role.MEMBER:
        return HttpResponseForbidden()
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return HttpResponseForbidden()
    target = get_object_or_404(Membership, crew=crew, user=target_user, status=Membership.Status.ACCEPTED)
    if target.role == Membership.Role.OWNER:
        return HttpResponseForbidden()
    if requester.role == Membership.Role.ADMIN and target.role == Membership.Role.ADMIN:
        return HttpResponseForbidden()
    target.delete()
    return HttpResponse('')


@login_required
def delete_crew(request, handle):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    get_object_or_404(
        Membership, crew=crew, user=request.user,
        role=Membership.Role.OWNER, status=Membership.Status.ACCEPTED
    )
    if request.method == 'POST':
        crew.delete()
        messages.success(request, f'Crew @{handle} has been deleted.')
        return redirect('crews:crews')
    return render(request, 'crew/delete_confirm.html', {'crew': crew})


@login_required
def set_admin(request, handle, username):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    requester = get_object_or_404(Membership, crew=crew, user=request.user, status=Membership.Status.ACCEPTED)
    if requester.role != Membership.Role.OWNER:
        return HttpResponseForbidden('Only the crew owner can assign admin roles.')
    target_user = get_object_or_404(User, username=username)
    target = get_object_or_404(Membership, crew=crew, user=target_user, status=Membership.Status.ACCEPTED)
    target.role = Membership.Role.ADMIN
    target.save()
    return HttpResponse(render_to_string(
        'member/card.html',
        {'m': target, 'crew': crew, 'membership': requester},
        request=request,
    ))


@login_required
def unset_admin(request, handle, username):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    requester = get_object_or_404(Membership, crew=crew, user=request.user, status=Membership.Status.ACCEPTED)
    if requester.role != Membership.Role.OWNER:
        return HttpResponseForbidden('Only the crew owner can remove admin roles.')
    target_user = get_object_or_404(User, username=username)
    target = get_object_or_404(Membership, crew=crew, user=target_user, status=Membership.Status.ACCEPTED)
    target.role = Membership.Role.MEMBER
    target.save()
    return HttpResponse(render_to_string(
        'member/card.html',
        {'m': target, 'crew': crew, 'membership': requester},
        request=request,
    ))

