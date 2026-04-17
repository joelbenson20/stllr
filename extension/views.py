from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from pages.models import Page, PageVote
import json
from pages.utils import get_canonical, verify_security, get_meta
from django.db.models import Count

@require_POST
def page_float(request):

    response = {}

    user = request.user
    
    payload = json.loads(request.body)
    page_id = payload.get('page_id')
    page = get_object_or_404(Page, id=page_id)

    # Check if there already exists a vote for the page by the user. If so, delete.
    if (user.page_votes.filter(page=page).exists()):
        vote = user.page_votes.get(page=page)
        vote.delete()
        response["status"] = "410"
    # Otherwise, create a new vote.
    else:
        vote = PageVote.objects.create(user=user, page=page)
        response["status"] = "201"

    response["num_votes"] = page.num_votes
    
    return JsonResponse(response)

@login_required
@require_POST
def extension(request):
    post_data = json.loads(request.body).get('pageData')

    url = post_data.get('url')
    title = post_data.get('title')
    fav_icon_url = post_data.get('favIconUrl')
    head = post_data.get('head')
    inner_text = post_data.get('innerText')

    try:
        canonical = get_canonical(url)
        page = Page.objects.get(canonical=canonical)
    except Page.DoesNotExist:
        page = None
    if (not page):
        meta = get_meta(head)
        image_url = meta['image_url']
        fav_icon_url = fav_icon_url or meta['fav_icon_url']
        page = Page.objects.create(canonical=canonical,
                                        title=title or meta['title'] or '',
                                        type=meta['type'] or '',
                                        description=meta['description'] or '',
                                        image_url=image_url or '',
                                        site_name=meta['site_name'] or '',
                                        fav_icon_url=fav_icon_url or '',
                                        inner_text=inner_text or meta['inner_text'] or '',
                                    )
        tags = meta['tags']
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
        'user': request.user,
    }
    
    return JsonResponse({
        'status': '200',
        'html': render_to_string('extension.html', context=context, request=request)
    })

@login_required
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})
