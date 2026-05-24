import secrets
import json
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.middleware.csrf import get_token
from pages.models import Page, Domain
from pages.utils import get_canonical, get_meta, get_domain_name, verify_security, InsecureURLError


@csrf_exempt
@login_required
@require_POST
def extension(request):
    data = json.loads(request.body).get('page').get('data')
    canonical = get_canonical(data.get('url'))
    try:
        page = Page.objects.get(canonical=canonical)
        if not page.is_active:
            return JsonResponse(
                {
                    'status': '403',
                    'html': render_to_string('extension/errors/inactive.html', request=request)
                }
            )
    except Page.DoesNotExist:
        scraped_data = get_meta(data.get('url'), data.get('head'))
        title = data.get('title') or scraped_data['title']
        type = scraped_data['type']
        description = scraped_data['description']
        content = "".join([ p for p in data.get('innerText').split('\n') if "." in p ])
        image_url = scraped_data['image_url']
        fav_icon_url = data.get('favIconUrl') or scraped_data['fav_icon_url']
        site_name = scraped_data.get('site_name')

        # Done by Claude, requires review
        try:
            verify_security(data.get('url'))
        except InsecureURLError as e:
            return JsonResponse(
                {
                    'status': '405',
                    'html': render_to_string('extension/errors/unsupported.html', request=request)
                }
            )

        domain_name = get_domain_name(data.get('url'))
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
            content=content or scraped_data['content'] or '',
        )

    # Default extension tab is 'forum'
    tab = request.GET.get('tab', 'forum')
    
    context = {
        'page': page,
        'tab': tab
    }

    html = None
    if (tab == 'forum'):
        html = render_to_string('extension/forum.html', context=context, request=request)
    elif (tab == 'room'):
        html = render_to_string('extension/room.html', context=context, request=request)
    elif (tab == 'similar'):
        # Done by Claude, requires review
        # similar_objects() has a taggit bug with generic FKs; query Page directly
        context['similar_pages'] = Page.objects.filter(
            tags__in=page.tags.all(), is_active=True
        ).exclude(pk=page.pk).distinct()
        html = render_to_string('extension/similar.html', context=context, request=request)

    return JsonResponse({
        'status': '200',
        'html': html
    })

def csrf_token(request):
    if (request.user.is_authenticated):
        return JsonResponse({
            'status': 200,
            'token': get_token(request)
        })
    else:
        return JsonResponse({
            'status': 403,
            'html': render_to_string('extension/errors/unauthenticated.html', request=request)
        })

@login_required
def ws_ticket(request):
    token = secrets.token_urlsafe(32)
    cache.set(f'ws_ticket:{token}', request.user.id, timeout=30)
    return JsonResponse({'ticket': token})

def loading(request):
    return JsonResponse({
        'status': '200',
        'html': render_to_string('extension/loading.html', request=request)
    })

def restricted(request):
    return JsonResponse({
        'status': '200',
        'html': render_to_string('extension/errors/restricted.html', request=request)
    })