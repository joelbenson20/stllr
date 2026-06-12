import random
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.postgres.search import SearchQuery
from django.db import connection
from django.db.models.expressions import RawSQL
from .models import Page, PagePin

def feed(request):
    sort = request.GET.get('sort', 'firmament')

    if sort == 'brightest':
        pages = Page.objects.order_by('-brightness', '?')
    elif sort == 'rising':
        pages = Page.objects.order_by('-rise', '?')
    else:
        seed = request.session.get('feed_seed', random.random())
        with connection.cursor() as cursor:
            cursor.execute('SELECT setseed(%s)', [seed])
        pages = Page.objects.order_by(RawSQL('brightness * RANDOM()', []).desc())

    query = request.GET.get('query')
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
