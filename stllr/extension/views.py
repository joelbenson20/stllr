from django.http import JsonResponse
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from pages.models import Page, Domain
import json
from pages.utils import get_canonical, get_meta, get_domain_name, verify_security, InsecureURLError
from django.db.models import Count


def get_csrf_token(request):
    if (request.user.is_authenticated):
        return JsonResponse(
            {
                'status': '200',
                'csrfToken': get_token(request)
            }
        )
    else:
        return JsonResponse(
            {
                'status': '401',
                'html': render_to_string('extension/errors/unauthenticated.html')
            }
        )
    
@csrf_exempt
@login_required
@require_POST
def extension(request):
    
    posted_data = json.loads(request.body).get('pageData')
    url = posted_data.get('url')
    canonical = get_canonical(url)
    domain_name = get_domain_name(url)

    try:
        page = Page.objects.get(canonical=canonical)
        if not page.is_active:
            return JsonResponse(
                {
                    'status': '403',
                    'html': render_to_string('extension/errors/inactive.html')
                }
            )
    except Page.DoesNotExist:
        scraped_data = get_meta(url, posted_data.get('head'))
        title = posted_data.get('title') or scraped_data['title']
        type = scraped_data['type']
        description = scraped_data['description']
        inner_text = posted_data.get('innerText')
        image_url = scraped_data['image_url']
        fav_icon_url = posted_data.get('favIconUrl') or scraped_data['fav_icon_url']
        site_name = scraped_data.get('site_name')

        try:
            verify_security(url) 
            verify_security(image_url)
            verify_security(fav_icon_url)
        except InsecureURLError as e:
            return JsonResponse(
                {
                    'status': '405',
                    'html': render_to_string('extension/errors/unsupported.html')
                }
            )


        domain, _ = Domain.objects.get_or_create(name=domain_name)
        if site_name and not domain.site_name:
            domain.site_name = site_name
            domain.save()
        if fav_icon_url and not domain.fav_icon_url:
            domain.fav_icon_url = fav_icon_url
            domain.save()

        page = Page.objects.create(
            canonical=canonical,
            title=title,
            type=type,
            description=description,
            image_url=image_url,
            domain = domain,
            inner_text=inner_text or scraped_data['inner_text'] or '',
        )

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
        'section': 'forum'
    }
    
    return JsonResponse({
        'status': '200',
        'html': render_to_string('extension/forum.html', context=context, request=request)
    })

@csrf_exempt
@require_POST
def forum(request):

    posted_data = json.loads(request.body).get('pageData')
    url = posted_data.get('url')
    canonical = get_canonical(url)

    try:
        page = Page.objects.get(canonical=canonical)
        if not page.is_active:
            return JsonResponse(
                {
                    'status': '403',
                    'html': render_to_string('extension/errors/inactive.html')
                }
            )
    except Page.DoesNotExist:
        return JsonResponse(
            {
                'status': '404',
                'html': render_to_string('extension/errors/undiscovered.html')
            }
        )
    
    context = {
        'page': page,
        'section': 'forum'
    }

    return JsonResponse(
        {
            'status': '200',
            'html': render_to_string('extension/forum.html', context=context, request=request)
        }
    )

@csrf_exempt
@require_POST
def relay(request):

    posted_data = json.loads(request.body).get('pageData')
    url = posted_data.get('url')
    canonical = get_canonical(url)

    try:
        page = Page.objects.get(canonical=canonical)
        if not page.is_active:
            return JsonResponse(
                {
                    'status': '403',
                    'html': render_to_string('extension/errors/inactive.html')
                }
            )
    except Page.DoesNotExist:
        return JsonResponse(
            {
                'status': '404',
                'html': render_to_string('extension/errors/undiscovered.html')
            }
        )
    
    context = {
        'page': page,
        'section': 'relay'
    }

    return JsonResponse(
        {
            'status': '200',
            'html': render_to_string('extension/relay.html', context=context, request=request)
        }
    )

@csrf_exempt
@require_POST
def similar(request):

    posted_data = json.loads(request.body).get('pageData')
    url = posted_data.get('url')
    canonical = get_canonical(url)

    try:
        page = Page.objects.get(canonical=canonical)
        if not page.is_active:
            return JsonResponse(
                {
                    'status': '403',
                    'html': render_to_string('extension/errors/inactive.html')
                }
            )
    except Page.DoesNotExist:
        return JsonResponse(
            {
                'status': '404',
                'html': render_to_string('extension/errors/undiscovered.html')
            }
        )
    
    context = {
        'page': page,
        'section': 'similar'
    }

    return JsonResponse(
        {
            'status': '200',
            'html': render_to_string('extension/similar.html', context=context, request=request)
        }
    )
