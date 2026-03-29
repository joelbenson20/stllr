from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from webpages.models import Webpage

@login_required
def index(request):

    webpages = Webpage.objects.all()
    
    context = {'webpages': webpages}

    return render(request, 'base.html', context=context)