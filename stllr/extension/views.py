from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from pages.models import Page, Domain
import json
from pages.utils import get_canonical, get_meta, get_domain_name, verify_security, InsecureURLError


@csrf_exempt
@login_required
@require_POST
def extension(request):

    data = json.loads(request.body).get('pageData')
    canonical = get_canonical(data.get('url'))
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
        scraped_data = get_meta(data.get('url'), data.get('head'))
        title = data.get('title') or scraped_data['title']
        type = scraped_data['type']
        description = scraped_data['description']
        inner_text = data.get('innerText')
        image_url = scraped_data['image_url']
        fav_icon_url = data.get('favIconUrl') or scraped_data['fav_icon_url']
        site_name = scraped_data.get('site_name')

        try:
            verify_security(data.get('url')) 
            verify_security(image_url)
            verify_security(fav_icon_url)
        except InsecureURLError as e:
            return JsonResponse(
                {
                    'status': '405',
                    'html': render_to_string('extension/errors/unsupported.html')
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
            inner_text=inner_text or scraped_data['inner_text'] or '',
        )

    tab = request.GET.get('tab')
    
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
        html = render_to_string('extension/similar.html', context=context, request=request)

    return JsonResponse({
        'status': '200',
        'html': html
    })