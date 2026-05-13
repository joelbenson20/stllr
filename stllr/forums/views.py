from django.shortcuts import render, get_object_or_404
from pages.models import Page

def forum(request):
    canonical = request.GET.get('p')
    page = get_object_or_404(Page, canonical=canonical)
    return render(request, 'forum.html', context={'page': page})