from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from webpages.models import Webpage
from users.models import WebpageVote
import json

@login_required
@require_POST
def webpage_vote(request):

    payload = json.loads(request.body)
    webpage_id = payload.get('webpage_id')

    user = request.user
    webpage = Webpage.objects.get(id=webpage_id)

    if (user.webpage_votes.filter(webpage=webpage).exists()):
        vote = user.webpage_votes.get(webpage=webpage)
        vote.delete()
        return JsonResponse({"message": "Vote removed"})
    else:
        vote = WebpageVote.objects.create(user=user, webpage=webpage)
        return JsonResponse({"message": "Vote added"})

@login_required
def api_index(request):

    webpages = Webpage.objects.all()
    
    context = {'webpages': webpages}

    return render(request, 'modules/feed.html', context=context)