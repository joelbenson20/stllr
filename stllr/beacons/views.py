from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from crews.models import Crew, Membership
from pages.models import Page
from .models import Beacon


@login_required
def beacons(request):
    return render(request, 'beacons.html')


def feed(request):
    beaconed_to_crew_id = request.GET.get('beaconed_to_crew_id')
    beaconed_to_user_id = request.GET.get('beaconed_to_user_id')

    if beaconed_to_crew_id:
        base_qs = Beacon.objects.filter(crew_id=beaconed_to_crew_id)
        attribution_qs = (
            base_qs.select_related('user')
            .order_by('page_id', 'user_id', '-created')
            .distinct('page_id', 'user_id')
        )
        attribution_template = 'beacon/attribution_users.html'
    elif beaconed_to_user_id:
        crew_ids = Membership.objects.filter(
            user_id=beaconed_to_user_id, status=Membership.Status.ACCEPTED
        ).values('crew_id')
        base_qs = Beacon.objects.filter(crew_id__in=crew_ids)
        attribution_qs = (
            base_qs.select_related('crew')
            .order_by('page_id', 'crew_id', '-created')
            .distinct('page_id', 'crew_id')
        )
        attribution_template = 'beacon/attribution_crews.html'
    else:
        return HttpResponse('')

    latest_per_page = (
        base_qs
        .order_by('page_id', '-created')
        .distinct('page_id')
        .values('id')
    )
    beacon_qs = (
        Beacon.objects
        .filter(id__in=latest_per_page)
        .select_related('page', 'page__domain', 'user', 'crew')
        .prefetch_related(
            Prefetch('page__beacons', queryset=attribution_qs, to_attr='attribution_beacons')
        )
        .order_by('-created')
    )

    paginator = Paginator(beacon_qs, 10)
    try:
        page = paginator.page(request.GET.get('p', 1))
    except (PageNotAnInteger, EmptyPage):
        return HttpResponse('')

    return render(request, 'beacon/list.html', {
        'beacons': page,
        'attribution_template': attribution_template,
    })


@login_required
@require_POST
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def create_beacon(request):
    page_id = request.POST.get('page_id')
    crew_id = request.POST.get('crew_id')

    if not (page_id and crew_id):
        return JsonResponse({'status': 400}, status=400)

    crew = get_object_or_404(Crew, id=crew_id)

    if not Membership.objects.filter(crew=crew, user=request.user, status=Membership.Status.ACCEPTED).exists():
        return JsonResponse({'status': 403}, status=403)

    page = get_object_or_404(Page, id=page_id)
    Beacon.objects.get_or_create(user=request.user, crew=crew, page=page)
    return JsonResponse({'status': 200}, status=200)


@login_required
@require_POST
def delete_beacon(request):
    page_id = request.POST.get('page_id')
    crew_id = request.POST.get('crew_id')
    if not (page_id and crew_id):
        return JsonResponse({'status': 400}, status=400)
    Beacon.objects.filter(user=request.user, page_id=page_id, crew_id=crew_id).delete()
    return JsonResponse({'status': 200}, status=200)


@login_required
def beacon_status(request):
    page_id = request.GET.get('page_id')
    if not page_id:
        return JsonResponse({'crew_ids': []})
    crew_ids = list(
        Beacon.objects.filter(user=request.user, page_id=page_id).values_list('crew_id', flat=True)
    )
    return JsonResponse({'crew_ids': crew_ids})
