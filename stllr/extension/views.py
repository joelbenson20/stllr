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
from pages.page_processors import youtube_processor
from pages.models import Page, Domain
from stella.models import Prompt
from pages.utils import get_canonical, get_domain_name, verify_supported, UnsupportedURLError

SUPPORTED_EXTENSION_VERSIONS = ['2.0']

@login_required #TODO: Unauthenticated users should get forbidden messages rather than redirect for all extension views
@require_POST
def extension(request):

    # Verify extension version supported
    extension_version = request.META.get('HTTP_X_EXTENSION_VERSION', '1.0') # Version 1.0 does not send the request header
    if extension_version not in SUPPORTED_EXTENSION_VERSIONS:
        return JsonResponse(
            {
                'status': 426,
                'html': render_to_string('extension/errors/update_required.html', request=request)
            },
            status=426
        )

    # Load page data
    data = json.loads(request.body).get('page').get('data')
    url = data.get('url')

    # Check URL against security policy
    try:
        verify_supported(url)
    except UnsupportedURLError:
        return JsonResponse(
            {
                'status': 405,
                'html': render_to_string('extension/errors/unsupported.html', request=request)
            },
            status=405
        )

    # Get or create domain
    domain_name = get_domain_name(url)
    domain, created = Domain.objects.get_or_create(
        name=domain_name
    )
    if created:
        domain.fav_icon_url = data.get('favIconUrl') or ''
        domain.site_name = data.get('siteName') or ''
        domain.save()
    
    # Get or create page
    canonical = get_canonical(url)
    protocol = urlparse(url).scheme.lower()
    try:
        page = Page.objects.get(canonical=canonical)

        # If new protocol, add to page's supported protocol
        if protocol and protocol not in page.supported_protocols:
            page.supported_protocols.append(protocol)
            page.save(update_fields=['supported_protocols'])
    except Page.DoesNotExist:

        # Process data for specific domains 
        if domain.name in ('youtube.com', 'youtu.be'):
            data = youtube_processor(url, data)

        page = Page.objects.create(
            canonical=canonical,
            title=data.get('title') or '',  #TODO: Better handling of null/blank?
            description=data.get('description') or '',
            image_url=data.get('imageUrl') or '',
            domain=domain,
            content=data.get('content') or '',
            inner_text=data.get('innerText') or '',
            supported_protocols=[protocol] if protocol else [],
        )

    # Default extension tab is 'forum'
    tab = request.GET.get('tab', 'frame')
    
    context = {
        'page': page,
        'tab': tab
    }

    html = None
    if (tab == 'frame'):
        context['prompts'] = Prompt.objects.filter(page=page).order_by('created')
        html = render_to_string('extension/frame.html', context=context, request=request)
    if (tab == 'forum'):
        html = render_to_string('extension/forum.html', context=context, request=request)
    elif (tab == 'room'):
        html = render_to_string('extension/room.html', context=context, request=request)
    elif (tab == 'nearby'):
        html = render_to_string('extension/nearby.html', context=context, request=request)

    return JsonResponse({
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