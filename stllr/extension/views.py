import secrets
import json
from urllib.parse import urlparse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.middleware.csrf import get_token
from pages.models import Page, Domain
from pages.utils import get_canonical, get_domain_name, verify_security, InsecureURLError  # Done by Claude, requires review

SUPPORTED_EXTENSION_VERSIONS = ['1.1']

@csrf_exempt
@login_required
@require_POST
def extension(request):
    extension_version = request.META.get('HTTP_X_EXTENSION_VERSION', '1.0') # Version 1.0 does not send the request header
    if extension_version not in SUPPORTED_EXTENSION_VERSIONS:
        return JsonResponse(
            {
                # Done by Claude, requires review
                'status': 400,
                'html': render_to_string('extension/errors/update_required.html', request=request)
            },
            status=400
        )

    data = json.loads(request.body).get('page').get('data')
    url = data.get('url')
    protocol = urlparse(url).scheme.lower()
    canonical = get_canonical(url)
    try:
        page = Page.objects.get(canonical=canonical)
        if protocol and protocol not in page.supported_protocols:
            page.supported_protocols.append(protocol)
            page.save(update_fields=['supported_protocols'])
        if not page.is_active:
            return JsonResponse(
                {
                    # Done by Claude, requires review
                    'status': 403,
                    'html': render_to_string('extension/errors/inactive.html', request=request)
                },
                status=403
            )
    except Page.DoesNotExist:
        # Done by Claude, requires review
        try:
            verify_security(url)
        except InsecureURLError:
            return JsonResponse(
                {
                    # Done by Claude, requires review
                    'status': 405,
                    'html': render_to_string('extension/errors/unsupported.html', request=request)
                },
                status=405
            )

        fav_icon_url = data.get('favIconUrl')
        site_name = data.get('siteName')
        domain_name = get_domain_name(url)
        domain, _ = Domain.objects.get_or_create(name=domain_name)
        if site_name and not domain.site_name:
            domain.site_name = site_name
            domain.save()
        if fav_icon_url and not domain.fav_icon_url:
            domain.fav_icon_url = fav_icon_url
            domain.save()

        page = Page.objects.create(
            canonical=canonical,
            title=data.get('title') or '',
            description=data.get('description') or '',
            image_url=data.get('imageUrl') or '',
            domain=domain,
            content=data.get('content') or '',
            supported_protocols=[protocol] if protocol else [],
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
        context['similar_pages'] = page.get_similar_pages()
        html = render_to_string('extension/similar.html', context=context, request=request)

    return JsonResponse({
        # Done by Claude, requires review
        'status': 200,
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
            # Done by Claude, requires review
            'status': 403,
            'html': render_to_string('extension/errors/unauthenticated.html', request=request)
        }, status=403)

@login_required
def ws_ticket(request):
    token = secrets.token_urlsafe(32)
    cache.set(f'ws_ticket:{token}', request.user.id, timeout=30)
    return JsonResponse({'ticket': token})

def restricted(request):
    return JsonResponse({
        'status': 200,
        'html': render_to_string('extension/errors/restricted.html', request=request)
    })