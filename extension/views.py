from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from forum.models import Page
from users.models import PageVote
import json
from .utils import get_canonical, verify_security

@login_required
@require_POST
def float_webpage(request):

    response = {}

    user = request.user
    
    payload = json.loads(request.body)
    webpage_id = payload.get('webpage_id')
    page = get_object_or_404(Page, id=webpage_id)

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

    response = {}
    payload = json.loads(request.body)
    webpage_data = payload.get('webpageData')

    verify_security(webpage_data['url'])
    canonical = get_canonical(webpage_data['url'])

    image_url = webpage_data.get('imageUrl', '')
    if (image_url):
        verify_security(image_url)

    webpage = Page.objects.get(canonical=canonical)

    if (not webpage):
        webpage = Page.objects.create(canonical=canonical,
                                        title=webpage_data['title'],
                                        description=webpage_data['description'],
                                        image_url=image_url,
                                        site_name=webpage_data.get('siteName', ''),
                                        fav_icon_url=webpage_data.get('favIconUrl', '')
                                        )
    
    context = {'webpage': webpage, 'user': request.user}
    
    response['html'] = render_to_string('extension.html', context=context, request=request)
    response['status'] = '200'

    return JsonResponse(response)

@login_required
@require_GET
def get_csrf_token(request):

    return JsonResponse({'csrfToken': get_token(request)})
