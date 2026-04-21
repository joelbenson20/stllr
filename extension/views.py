from django.http import JsonResponse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from pages.models import Page, Domain
import json
from pages.utils import get_canonical, get_meta, get_domain_name
from django.db.models import Count


@login_required
@require_POST
def extension(request):
    
    posted_data = json.loads(request.body).get('pageData')

    url = posted_data.get('url')
    canonical = get_canonical(url)
    domain_name = get_domain_name(url)
    head = posted_data.get('head')
    inner_text = posted_data.get('innerText')

    page = None
    try:
        page = Page.objects.get(canonical=canonical)
    except Page.DoesNotExist:
        scraped_data = get_meta(url, head)
        image_url = scraped_data['image_url']
        fav_icon_url = posted_data.get('favIconUrl') or scraped_data['fav_icon_url'] or ''
        site_name = scraped_data.get('site_name') or ''

        domain, created = Domain.objects.get_or_create(name=domain_name)
        # Update domain if new information
        if not domain.site_name and site_name:
            domain.site_name = site_name
            domain.save()
        if not domain.fav_icon_url and fav_icon_url:
            domain.fav_icon_url = fav_icon_url
            domain.save()

        page = Page.objects.create(
            canonical=canonical,
            title= posted_data.get('title') or scraped_data['title'] or '',
            type=scraped_data['type'] or '',
            description=scraped_data['description'] or '',
            image_url=image_url or '',
            domain = domain,
            inner_text=inner_text or scraped_data['inner_text'] or '',
        )

        tags = scraped_data['tags'] or ''
        if tags:
            raw_tags = tags
            tags_list = [t.strip() for t in raw_tags.split(',') if t.strip()] if isinstance(raw_tags, str) else raw_tags
            page.tags.set(tags_list)

    # Get top 3 similar pages based on number of shared tags
    page_tags_ids = page.tags.values_list('id', flat=True)
    similar_pages = Page.objects.filter(
        tags__in=page_tags_ids
    ).exclude(id=page.id)
    similar_pages = similar_pages.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags')[:3]
    
    context = {
        'page': page,
        'similar_pages': similar_pages,
    }
    
    return JsonResponse({
        'status': '200',
        'html': render_to_string('extension.html', context=context, request=request)
    })

@login_required
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})
