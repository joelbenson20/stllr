from django.shortcuts import render, get_object_or_404
from .models import Page
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from taggit.models import Tag
from django.http import JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .utils import pages_stochastic
from django_ratelimit.decorators import ratelimit
from django.contrib.postgres.search import SearchQuery


def feed_view(request):
    sort = None
    query = None
    tag = None

    sort = request.GET.get('sort', 'firmament')
    if sort == 'brightest':
        pages = Page.objects.order_by('brightness_index')
    elif sort == 'rising':
        pages = Page.objects.order_by('-rise')
    else:
        pages = pages_stochastic()

    tag_slug = request.GET.get('tag')
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        pages = pages.filter(tags__in=[tag])

    query = request.GET.get('query')
    if query:
        search_query = SearchQuery(query, search_type='websearch')
        pages = pages.filter(search_vector=search_query)
    
    paginator = Paginator(pages, 100)
    p = request.GET.get('p')
    cards_only = request.GET.get('cards_only')

    try:
        pages = paginator.page(p)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        if cards_only:
            return HttpResponse('')
        pages = paginator.page(paginator.num_pages)

    if cards_only:
        return render(request, 'page/list.html', {'pages': pages})
    
    return render(request, 'page/feed.html', {
        'pages': pages,
        'query': query,
        'tag': tag,
        'sort': sort
    })

def page_detail(request):
    canonical = request.GET.get('p')
    page = get_object_or_404(Page, canonical=canonical)
    return render(request, 'page/detail.html', context={"page": page})

@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def page_star(request):
    page_id = request.POST.get('id')
    action = request.POST.get('action')
    if page_id and action:
        try:
            page = Page.objects.get(id=page_id)
            if action == 'star':
                page.users_star.add(request.user)
            else:
                page.users_star.remove(request.user)
            return JsonResponse({'status': '200'})
        except Page.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})
