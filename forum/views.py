from django.shortcuts import redirect, render, get_object_or_404
from django.test import tag
from .models import Page
from django.views.decorators.http import require_POST
from .utils import getMetadata, get_canonical, verify_security
from django.db.models import Count
from django.urls import reverse
from taggit.models import Tag

def index(request, tag_slug=None):
    pages = (
        Page.objects
        .annotate(vote_count=Count('votes'))
        .filter(vote_count__gt=0)
        .order_by('-vote_count')
    )
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        pages = pages.filter(tags__in=[tag])
    context = {
        'pages': pages,
        'tag': tag,
    }
    return render(request, 'base.html', context=context)

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

@require_POST
def page_float(request):
    user = request.user
    url = request.POST.get('url')
    canonical = get_canonical(url)
    try:
        page = Page.objects.get(canonical=canonical)
        return redirect(page)
    except Page.DoesNotExist:
        pass
    try:
        metadata = getMetadata(url)
    except Exception as e:
        print(f"Error fetching metadata for {url}: {e}")
        return redirect(reverse('forum:index'))
    # With canonical url pulled from metadata, check for page again
    try:
        page = Page.objects.get(canonical=metadata['canonical'])
        return redirect(page)
    except:
        pass
    verify_security(metadata['image_url'])
    verify_security(metadata['fav_icon_url'])
    page = Page.objects.create(canonical=metadata['canonical'],
                                title=metadata['title'],
                                type=metadata['type'],
                                tags=metadata['tags'],
                                description=metadata['description'],
                                image_url=metadata['image_url'],
                                site_name=metadata.get('site_name', ''),
                                fav_icon_url=metadata.get('fav_icon_url', '')
                                )
    # Add vote for the webpage by the user.
    if (not user.page_votes.filter(page=page).exists()):
        user.page_votes.create(page=page)
    return redirect(page)
