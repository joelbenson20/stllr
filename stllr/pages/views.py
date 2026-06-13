import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.postgres.search import SearchQuery
from django.db import connection
from django.db.models.expressions import RawSQL
from .models import Page, PagePin

def feed(request):
    query = request.GET.get('query', '')
    sort = request.GET.get('sort', 'firmament')
    seed = float(request.GET.get('seed', random.random()))
    starred_by = request.GET.get('starred_by')
    near_to = request.GET.get('near_to')

    pages = None

    if near_to:
        source_page = get_object_or_404(Page, id=near_to)
        pages = source_page.get_nearby_pages()
    elif starred_by:
        profile_user = get_object_or_404(get_user_model(), username=starred_by)
        pages = Page.objects.filter(stars__user=profile_user).order_by('-stars__created')
    else:
        if sort == 'firmament':
            with connection.cursor() as cursor:
                cursor.execute('SELECT setseed(%s)', [seed])
                pages = Page.objects.order_by(RawSQL('brightness * RANDOM()', []).desc())
        elif sort == 'brightest':
            pages = Page.objects.order_by('-brightness', '?')
        elif sort == 'rising':
            pages = Page.objects.order_by('-rise', '?')

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
