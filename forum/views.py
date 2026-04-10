from django.shortcuts import redirect, render
from .models import Page
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .utils import getOGMetaData, get_canonical, verify_security
from django.db.models import Count

def index(request):
    pages = (
        Page.objects
        .annotate(vote_count=Count('votes'))
        .filter(vote_count__gt=0)
        .order_by('-vote_count')[:100]
    )
    context = {'pages': pages}
    return render(request, 'base.html', context=context)

def page_forum(request):
    canonical = request.GET.get('page')
    page = get_object_or_404(Page, canonical=canonical)
    context = {
        "page": page,
    }
    return render(request, 'page/detail.html', context=context)

@require_POST
def page_float(request):
    user = request.user
    url = request.POST.get('url')
    canonical = get_canonical(url)
    try:
        webpage = Page.objects.get(canonical=canonical)
        return redirect('webpages:detail', pk=webpage.pk)
    except Page.DoesNotExist:
        pass
    try:
        og_metadata = getOGMetaData(url)
    except Exception as e:
        print(f"Error fetching metadata for {url}: {e}")
        return redirect('index')
    verify_security(og_metadata['image_url'])
    verify_security(og_metadata['fav_icon_url'])
    webpage = Page.objects.create(canonical=og_metadata['canonical'],
                                title=og_metadata['title'],
                                description=og_metadata['description'],
                                image_url=og_metadata['image_url'],
                                site_name=og_metadata.get('site_name', ''),
                                fav_icon_url=og_metadata.get('fav_icon_url', '')
                                )
    # Add vote for the webpage by the user.
    if (not user.page_votes.filter(page=webpage).exists()):
        user.page_votes.create(page=webpage)
    return redirect('forum:page_forum', pk=webpage.pk)
