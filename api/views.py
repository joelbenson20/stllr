import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from webpages.models import Webpage

@login_required
@require_POST
def webpage_vote(request):

    data = json.loads(request.body)
    print(f"Received vote for webpage ID: {data.get('webpage_id')}")
    print(f"User: {request.user}")

    return JsonResponse({"message": "Vote received"})

@login_required
def api_index(request):

    webpages = Webpage.objects.all()
    
    context = {'webpages': webpages}

    return render(request, 'modules/feed.html', context=context)