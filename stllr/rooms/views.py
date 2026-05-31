from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from pages.models import Page
from .consumers import _get_users


def room(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    return render(request, 'room.html', context={'page': page})


def room_count(request):
    ids = [i.strip() for i in request.GET.get('ids', '').split(',') if i.strip()]
    counts = {page_id: len(_get_users(f'room_{page_id}')) for page_id in ids}
    return JsonResponse(counts)