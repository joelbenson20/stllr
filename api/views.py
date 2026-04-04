from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from webpages.models import Webpage
from users.models import WebpageVote
import json
from .utils import get_canonical, verify_security

@login_required
@require_POST
def webpage_vote(request):

    response = {}

    payload = json.loads(request.body)
    webpage_id = payload.get('webpage_id')
    user = request.user
    webpage = Webpage.objects.get(id=webpage_id)

    # Check if there already exists a vote for the page by the user. If so, delete.
    if (user.webpage_votes.filter(webpage=webpage).exists()):
        vote = user.webpage_votes.get(webpage=webpage)
        vote.delete()
        response["status"] = "410"
    # Otherwise, create a new vote.
    else:
        vote = WebpageVote.objects.create(user=user, webpage=webpage)
        response["status"] = "201"

    response["num_votes"] = webpage.num_votes
    
    return JsonResponse(response)

@login_required
def extension(request):

    response = {}
    webpage_data = json.loads(request.headers.get('webpageData'))

    verify_security(webpage_data['url'])
    canonical = get_canonical(webpage_data['url'])

    image_url = webpage_data.get('imageUrl', '')
    if (image_url):
        verify_security(image_url)

    webpage = Webpage.objects.filter(canonical=canonical).first()

    if (not webpage):
        webpage = Webpage.objects.create(canonical=canonical,
                                        title=webpage_data['title'],
                                        description=webpage_data['description'],
                                        image_url=image_url)
    
    context = {'webpages': [webpage], 'user': request.user}
    
    response['html'] = render_to_string('extension.html', context=context, request=request)
    response['status'] = '200'

    return JsonResponse(response)