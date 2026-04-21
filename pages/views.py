from django.shortcuts import render, get_object_or_404
from .models import Page
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from taggit.models import Tag
from django.http import JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse


def page_feed(request, tag_slug=None):
    pages = (
        Page.objects
        .filter(total_stars__gt=0)
        .order_by('-total_stars')
    )
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        pages = pages.filter(tags__in=[tag])

    paginator = Paginator(pages, 10)
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
        return render(
            request,
            'page/list.html',
            {'pages': pages}
        )
    return render(
        request,
        'page/feed.html',
        {
            'pages': pages,
            'tag': tag
         }
    )

def page_detail(request):
    canonical = request.GET.get('p')
    page = get_object_or_404(Page, canonical=canonical)

    # Get top 3 similar pages based on number of shared tags
    page_tags_ids = page.tags.values_list('id', flat=True)
    similar_pages = Page.objects.filter(
        tags__in=page_tags_ids
    ).exclude(id=page.id)
    similar_pages = similar_pages.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags')[:3]

    context = {
        "page": page,
        "similar_pages": similar_pages,
    }
    return render(request, 'page/detail.html', context=context)

@login_required
@require_POST
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
