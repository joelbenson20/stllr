from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery
from pages.models import Page
from users.models import Contact, Action
from taggit.models import Tag

def index(request):
    sort = None
    query = None
    tag = None

    sort = request.GET.get('sort', 'firmament')
    if sort == 'brightest':
        pages = Page.objects.order_by('brightness_index')
    elif sort == 'rising':
        pages = Page.objects.order_by('-rise')
    else:
        pages = Page.firmament.all()

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
    
    contact_actions = []
    if request.user.is_authenticated:
        contacts = Contact.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user),
            status=Contact.Status.ACCEPTED
        ).values_list('from_user', 'to_user')
        contact_ids = {uid for pair in contacts for uid in pair} - {request.user.id}
        contact_actions = Action.objects.filter(
            user_id__in=contact_ids
        ).select_related('user', 'page').order_by('user', '-created').distinct('user')

    return render(request, 'index.html', {
        'pages': pages,
        'query': query,
        'tag': tag,
        'sort': sort,
        'contact_actions': contact_actions
    })