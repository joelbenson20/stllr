from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from .forms import CrewForm
from .models import Crew, Membership


def crews(request):
    return render(request, 'crews.html')


def crew_detail(request, handle):
    crew = get_object_or_404(Crew, handle__iexact=handle)
    membership = None
    if request.user.is_authenticated:
        membership = Membership.objects.filter(crew=crew, user=request.user).first()
    members = (
        Membership.objects
        .filter(crew=crew, status=Membership.Status.ACCEPTED)
        .select_related('user')
        .order_by('joined')
    )
    return render(request, 'crew/detail.html', {
        'crew': crew,
        'membership': membership,
        'members': members,
    })



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


def find_crews(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        crews = Crew.objects.filter(
            Q(name__icontains=q) | Q(handle__icontains=q)
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
    user = get_object_or_404(get_user_model(), username=username)
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