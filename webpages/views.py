from django.shortcuts import render
from .models import Webpage
from .utils import getOGMetaData
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

app_name = 'webpages'

@login_required
@require_POST
def float_webpage(request):

    print(request.POST)

    # Get url from request body and get OG metadata
    url = request.POST.get('url')
    getOGMetaData(url)

    return


def detail(request, pk):

    context = {
        "webpage": Webpage.objects.get(pk=pk)
    }

    return render(request, 'webpages/detail.html', context=context)