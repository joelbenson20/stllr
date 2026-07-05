from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import CrewForm
from .models import Crew, Membership


def _safe_next(request, fallback):
    next_url = request.POST.get('next', '')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return fallback

User = get_user_model()


def crews(request):
    return render(request, 'crews.html')


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
    crew = get_object_or_404(Crew, handle=handle)
    membership = get_object_or_404(Membership, crew=crew, user=request.user, status=Membership.Status.ACTIVE)
    if membership.role != Membership.Role.OWNER:
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


def _crew_base_context(request, handle):
    crew = get_object_or_404(Crew, handle=handle)
    membership = None
    if request.user.is_authenticated:
        request_user_membership = Membership.objects.filter(crew=crew, user=request.user).first()
    return crew, {'crew': crew, 'request_user_membership': request_user_membership}


def crew_beacons(request, handle):
    _, context = _crew_base_context(request, handle)
    context['active_tab'] = 'beacons'
    return render(request, 'crew/detail.html', context)


def crew_stars(request, handle):
    _, context = _crew_base_context(request, handle)
    context['active_tab'] = 'stars'
    return render(request, 'crew/detail.html', context)


def crew_mentions(request, handle):
    _, context = _crew_base_context(request, handle)
    context['active_tab'] = 'mentions'
    return render(request, 'crew/detail.html', context)


def crew_members(request, handle):
    crew, context = _crew_base_context(request, handle)
    context['active_tab'] = 'members'
    context['memberships'] = (
        Membership.objects
        .filter(crew=crew, status=Membership.Status.ACTIVE)
        .select_related('user')
        .order_by('joined')
    )
    if request.user.is_authenticated and request.user.pk in crew.admin_pks:
        context['memberships_requested'] = (
            Membership.objects
            .filter(crew=crew, status=Membership.Status.REQUESTED)
            .select_related('user')
            .order_by('created')
        )
    return render(request, 'crew/detail.html', context)


@login_required
def scout_members(request, handle):
    crew = get_object_or_404(Crew, handle=handle)
    requester_membership = Membership.objects.filter(
        crew=crew, user=request.user, status=Membership.Status.ACTIVE
    ).first()
    if not requester_membership or requester_membership.role not in [Membership.Role.ADMIN, Membership.Role.OWNER]:
        return redirect(crew.get_absolute_url())
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        users = (
            User.objects
            .filter(username__icontains=q)
            .exclude(pk=request.user.pk)
            .exclude(pk__in=Membership.objects.filter(crew=crew, status=Membership.Status.ACTIVE).values('user_id'))
            [:20]
        )
        memberships = {}
        for membership in Membership.objects.filter(crew=crew, user__in=users):
            memberships[membership.user_id] = membership

        results = [{'user': user, 'membership': memberships.get(user.pk)} for user in users]
    return render(request, 'scout_members.html', {'crew': crew, 'q': q, 'results': results})


def find_crews(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        crews = Crew.objects.filter(
            Q(name__icontains=q) | Q(handle__icontains=q) | Q(bio__icontains=q)
        )[:20]
        memberships = {}
        if request.user.is_authenticated:
            for membership in Membership.objects.filter(crew__in=crews, user=request.user):
                memberships[membership.crew_id] = membership
        results = [{'crew': crew, 'membership': memberships.get(crew.pk)} for crew in crews]
    return render(request, 'find_crews.html', {'q': q, 'results': results})


@require_POST
@login_required
def join_crew(request, handle):
    crew = get_object_or_404(Crew, handle=handle)
    if Membership.objects.filter(crew=crew, user=request.user).exists():
        return HttpResponseForbidden()
    status = Membership.Status.ACTIVE if crew.is_open else Membership.Status.REQUESTED
    Membership.objects.create(
        crew=crew, user=request.user, status=status, role=Membership.Role.MEMBER,
    )
    return redirect(_safe_next(request, crew.get_absolute_url()))


@require_POST
@login_required
def leave_crew(request, handle):
    crew = get_object_or_404(Crew, handle=handle)
    membership = get_object_or_404(Membership, crew=crew, user=request.user)
    if membership.role == Membership.Role.OWNER:
        return HttpResponseForbidden()
    membership.delete()
    return redirect(_safe_next(request, crew.get_absolute_url()))


@require_POST
@login_required
def send_invite(request, handle, username):
    crew = get_object_or_404(Crew, handle=handle)
    if request.user.pk not in crew.admin_pks:
        return HttpResponseForbidden()
    user = get_object_or_404(User, username=username)
    if Membership.objects.filter(crew=crew, user=user, status__in=[
        Membership.Status.ACTIVE, Membership.Status.REQUESTED,
    ]).exists():
        return HttpResponseForbidden()
    membership, _ = Membership.objects.get_or_create(
        crew=crew, user=user,
        defaults={'status': Membership.Status.INVITED, 'role': Membership.Role.MEMBER},
    )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'crew/buttons/invitation.html',
            {'crew': crew, 'membership': membership, 'user': user},
            request=request,
        ))
    return redirect(crew.get_absolute_url())


@require_POST
@login_required
def cancel_invite(request, handle, username):
    crew = get_object_or_404(Crew, handle=handle)
    if request.user.pk not in crew.admin_pks:
        return HttpResponseForbidden()
    target_user = get_object_or_404(User, username=username)
    get_object_or_404(Membership, crew=crew, user=target_user, status=Membership.Status.INVITED).delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'crew/buttons/invitation.html',
            {'crew': crew, 'user': target_user},
            request=request,
        ))
    return redirect(crew.get_absolute_url())


@require_POST
@login_required
def accept_invite(request, handle):
    crew = get_object_or_404(Crew, handle=handle)
    membership = get_object_or_404(
        Membership, crew=crew, user=request.user, status=Membership.Status.INVITED
    )
    membership.status = Membership.Status.ACTIVE
    membership.save()
    return redirect(_safe_next(request, 'crews:crews'))


@require_POST
@login_required
def decline_invite(request, handle):
    crew = get_object_or_404(Crew, handle=handle)
    get_object_or_404(Membership, crew=crew, user=request.user, status=Membership.Status.INVITED).delete()
    return redirect(_safe_next(request, 'crews:crews'))


@require_POST
@login_required
def admit_member(request, handle, username):
    crew = get_object_or_404(Crew, handle=handle)
    requester_membership = get_object_or_404(Membership, crew=crew, user=request.user, status=Membership.Status.ACTIVE)
    if requester_membership.role not in [Membership.Role.ADMIN, Membership.Role.OWNER]:
        return HttpResponseForbidden()
    target_user = get_object_or_404(User, username=username)
    target = get_object_or_404(Membership, crew=crew, user=target_user, status=Membership.Status.REQUESTED)
    target.status = Membership.Status.ACTIVE
    target.save()
    return redirect(_safe_next(request, reverse('crews:crew_members', kwargs={'handle': handle})))


@require_POST
@login_required
def remove_member(request, handle, username):
    crew = get_object_or_404(Crew, handle=handle)
    requester_membership = Membership.objects.filter(
        crew=crew, user=request.user, status=Membership.Status.ACTIVE
    ).first()
    if not requester_membership or requester_membership.role not in [Membership.Role.ADMIN, Membership.Role.OWNER]:
        return HttpResponseForbidden()
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return HttpResponseForbidden()
    target_membership = get_object_or_404(Membership, crew=crew, user=target_user, status=Membership.Status.ACTIVE)
    if target_membership.role == Membership.Role.OWNER:
        return HttpResponseForbidden()
    if requester_membership.role == Membership.Role.ADMIN and target_membership.role == Membership.Role.ADMIN:
        return HttpResponseForbidden()
    target_membership.delete()
    return redirect(_safe_next(request, reverse('crews:crew_members', kwargs={'handle': handle})))


@require_POST
@login_required
def deny_member(request, handle, username):
    crew = get_object_or_404(Crew, handle=handle)
    requester_membership = Membership.objects.filter(
        crew=crew, user=request.user, status=Membership.Status.ACTIVE
    ).first()
    if not requester_membership or requester_membership.role not in [Membership.Role.ADMIN, Membership.Role.OWNER]:
        return HttpResponseForbidden()
    target_user = get_object_or_404(User, username=username)
    Membership.objects.filter(crew=crew, user=target_user, status=Membership.Status.REQUESTED).delete()
    return redirect(_safe_next(request, reverse('crews:crew_members', kwargs={'handle': handle})))


@require_POST
@login_required
def set_admin(request, handle, username):
    crew = get_object_or_404(Crew, handle=handle)
    requester_membership = get_object_or_404(Membership, crew=crew, user=request.user, status=Membership.Status.ACTIVE)
    if requester_membership.role != Membership.Role.OWNER:
        return HttpResponseForbidden('Only the crew owner can assign admin roles.')
    target_user = get_object_or_404(User, username=username)
    target_membership = get_object_or_404(Membership, crew=crew, user=target_user, status=Membership.Status.ACTIVE)
    target_membership.role = Membership.Role.ADMIN
    target_membership.save()
    return redirect(_safe_next(request, reverse('crews:crew_members', kwargs={'handle': handle})))


@require_POST
@login_required
def unset_admin(request, handle, username):
    crew = get_object_or_404(Crew, handle=handle)
    requester_membership = get_object_or_404(Membership, crew=crew, user=request.user, status=Membership.Status.ACTIVE)
    if requester_membership.role != Membership.Role.OWNER:
        return HttpResponseForbidden('Only the crew owner can remove admin roles.')
    target_user = get_object_or_404(User, username=username)
    target_membership = get_object_or_404(Membership, crew=crew, user=target_user, status=Membership.Status.ACTIVE)
    target_membership.role = Membership.Role.MEMBER
    target_membership.save()
    return redirect(_safe_next(request, reverse('crews:crew_members', kwargs={'handle': handle})))


@login_required
def set_owner(request, handle, username):
    crew = get_object_or_404(Crew, handle=handle)
    requester_membership = get_object_or_404(Membership, crew=crew, user=request.user, status=Membership.Status.ACTIVE)
    if requester_membership.role != Membership.Role.OWNER:
        return HttpResponseForbidden('Only the crew owner can transfer ownership.')
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        target_membership = get_object_or_404(Membership, crew=crew, user=target_user, status=Membership.Status.ACTIVE)
        target_membership.role = Membership.Role.OWNER
        target_membership.save()
        requester_membership.role = Membership.Role.ADMIN
        requester_membership.save()
        return redirect(_safe_next(request, reverse('crews:crew_members', kwargs={'handle': handle})))
    return render(request, 'crew/confirmations/set_owner.html', {'crew': crew, 'target_user': target_user})


@login_required
def delete_crew(request, handle):
    crew = get_object_or_404(Crew, handle=handle)
    get_object_or_404(
        Membership, crew=crew, user=request.user,
        role=Membership.Role.OWNER, status=Membership.Status.ACTIVE
    )
    if request.method == 'POST':
        crew.delete()
        messages.success(request, f'Crew @{handle} has been deleted.')
        return redirect('crews:crews')
    return render(request, 'crew/confirmations/delete.html', {'crew': crew})

