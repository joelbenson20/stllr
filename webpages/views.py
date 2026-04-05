from django.shortcuts import render
from .models import Webpage

# Create your views here.
def webpage_detail(request, pk):

    context = {
        "webpage": Webpage.objects.get(pk=pk)
    }

    return render(request, 'webpage_detail.html', context=context)