from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from forum.models import Page
from users.models import PageVote
import json
from forum.utils import get_canonical, verify_security

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

@require_POST
def extension(request):

    response = {}
    page_data = json.loads(request.body).get('pageData')

    verify_security(page_data['url'])
    canonical = get_canonical(page_data['url'])

    image_url = page_data.get('imageUrl', '')
    fav_icon_url = page_data.get('favIconUrl', '')
    verify_security(image_url)
    verify_security(fav_icon_url)

    try:
        page = Page.objects.get(canonical=canonical)
    except Page.DoesNotExist:
        page = None

    if (not page):
        page = Page.objects.create(canonical=canonical,
                                        title=page_data['title'],
                                        description=page_data['description'],
                                        image_url=image_url,
                                        site_name=page_data.get('siteName', ''),
                                        fav_icon_url=fav_icon_url
                                    )
    
    context = {'page': page, 'user': request.user}
    
    response['html'] = render_to_string('extension.html', context=context, request=request)
    response['status'] = '200'

    return JsonResponse(response)

@login_required
def get_csrf_token(request):

    return JsonResponse({'csrfToken': get_token(request)})
