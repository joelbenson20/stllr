from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from webpages.models import Webpage

@login_required
def index(request):

    webpages = (
        Webpage.objects
        .annotate(vote_count=Count('votes'))
        .filter(vote_count__gt=0)
        .order_by('-vote_count')[:100]
    )
    
    context = {'webpages': webpages}

    return render(request, 'base.html', context=context)