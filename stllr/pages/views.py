import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.postgres.search import SearchQuery
from django.db import connection
from django.db.models import Count, ExpressionWrapper, FloatField, Max
from django.db.models.expressions import RawSQL
from django.db.models.functions import Random
from .models import Page, PagePin
from crews.models import Crew, Membership

def feed(request):
    query = request.GET.get('query', '')
    sort = request.GET.get('sort', 'firmament')
    seed = float(request.GET.get('seed', random.random()))
    starred_by_user_id = request.GET.get('starred_by_user_id')
    starred_by_crew_id = request.GET.get('starred_by_crew_id')
    beaconed_by_crew_id = request.GET.get('beaconed_by_crew_id')
    beaconed_to_user_id = request.GET.get('beaconed_to_user_id')
    near_page_id = request.GET.get('near_page_id')

    pages = None

    if near_page_id:
        source_page = get_object_or_404(Page, id=near_page_id)
        pages = source_page.get_nearby_pages()
    elif starred_by_user_id:
        profile_user = get_object_or_404(get_user_model(), id=starred_by_user_id)
        pages = Page.objects.filter(stars__user=profile_user).order_by('-stars__created')
    elif starred_by_crew_id:
        crew = get_object_or_404(Crew, id=starred_by_crew_id)
        member_user_ids = crew.memberships.filter(status=Membership.Status.ACTIVE).values('user')
        with connection.cursor() as cursor:
            cursor.execute('SELECT setseed(%s)', [seed])
        pages = (
            Page.objects
            .filter(stars__user__in=member_user_ids)
            .annotate(firmament_score=ExpressionWrapper(Count('stars') * Random(), output_field=FloatField()))
            .order_by('-firmament_score')
        )
    elif beaconed_by_crew_id:
        crew = get_object_or_404(Crew, id=beaconed_by_crew_id)
        pages = (
            Page.objects
            .filter(beacons__crew=crew)
            .annotate(last_beaconed=Max('beacons__created'))
            .order_by('-last_beaconed')
        )
    elif beaconed_to_user_id:
        target_user = get_object_or_404(get_user_model(), id=beaconed_to_user_id)
        crew_ids = Membership.objects.filter(
            user=target_user, status=Membership.Status.ACTIVE
        ).values('crew_id')
        pages = (
            Page.objects
            .filter(beacons__crew_id__in=crew_ids)
            .annotate(last_beaconed=Max('beacons__created'))
            .order_by('-last_beaconed')
        )
    else:
        if sort == 'firmament':
            with connection.cursor() as cursor:
                cursor.execute('SELECT setseed(%s)', [seed])
                pages = Page.objects.order_by(RawSQL('brightness * RANDOM()', []).desc())
        elif sort == 'brightest':
            pages = Page.objects.order_by('-brightness', '?')
        elif sort == 'rising':
            pages = Page.objects.order_by('-rising_score', '?')
        elif sort == 'forging':
            pages = Page.objects.order_by('-forging_score', '?')
        elif sort == 'poppin':
            pages = Page.objects.order_by('-poppin_score', '?')

        if query:
            pages = pages.filter(search_vector=SearchQuery(query, search_type='websearch'))

    paginator = Paginator(pages, 5)
    
    try:
        pages = paginator.page(request.GET.get('p', 1))
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        return HttpResponse('')

    return render(request, 'page/list.html', {'pages': pages})



@login_required
@require_POST
def toggle_pin(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    action = request.POST.get('action')
    if action == 'pin':
        PagePin.objects.get_or_create(page=page, user=request.user)
    elif action == 'unpin':
        pin = PagePin.objects.filter(page=page, user=request.user).first()
        if pin:
            pin.delete()
    else:
        return JsonResponse({'status': 400}, status=400)
    return JsonResponse({'status': 200}, status=200)
