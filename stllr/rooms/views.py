from django.shortcuts import render, get_object_or_404
from pages.models import Page


def room(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    return render(request, 'room.html', context={'page': page})

