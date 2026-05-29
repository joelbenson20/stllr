from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery
from pages.models import Page
from django.contrib.auth.decorators import login_required
from taggit.models import Tag

def home(request):

    pages = Page.firmament.firmament()

    paginator = Paginator(pages, 20)
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

    return render(request, 'home.html', {'pages': pages})

def explore(request):
    sort = request.GET.get('sort', 'firmament')
    if sort == 'brightest':
        pages = Page.objects.order_by('-brightness', '?')
    elif sort == 'rising':
        pages = Page.objects.order_by('-rise', '?')
    else:
        pages = Page.firmament.firmament()

    tag_slug = request.GET.get('tag')
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        pages = pages.filter(tags__in=[tag])

    query = request.GET.get('query')
    if query:
        search_query = SearchQuery(query, search_type='websearch')
        pages = pages.filter(search_vector=search_query)

    paginator = Paginator(pages, 20)
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

    return render(request, 'explore.html', {
        'pages': pages,
        'query': query,
        'tag': tag,
        'sort': sort,
    })

@login_required
def contacts(request):
    return render(request, 'contacts.html')

@login_required
def comms(request):
    from comms.models import Notification
    user_notifications = list(
        Notification.objects
        .filter(recipient=request.user)
        .prefetch_related('notification_actors__actor')
    )
    Notification.objects.filter(recipient=request.user).update(read=True)
    return render(request, 'comms.html', {'user_notifications': user_notifications})

@login_required
def pins(request):
    pinned_pages = Page.objects.filter(pins__user=request.user).order_by('-pins__created')
    return render(request, 'pins.html', {'pages': pinned_pages})

def policy(request, policy):
    if (policy == 'privacy-policy'):
        return render(request, 'policies/generated-privacy-policy.html')
    elif (policy == 'user-agreement'):
        return render(request, 'policies/user-agreement.html')
    else:
        raise Http404(f"Policy {policy} was not found.")