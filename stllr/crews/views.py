from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CrewForm
from .models import Crew, Membership


def crews(request):
    crews_list = (
        Crew.objects
        .annotate(member_count=Count('memberships', filter=Q(memberships__status=Membership.Status.ACCEPTED)))
        .order_by('-created')
    )
    return render(request, 'crews.html', {'crews_list': crews_list})


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
