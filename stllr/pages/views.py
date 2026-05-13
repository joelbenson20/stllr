from django.shortcuts import render, get_object_or_404
from .models import Page
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from taggit.models import Tag
from django.http import JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .utils import pages_stochastic
from django_ratelimit.decorators import ratelimit
from django.contrib.postgres.search import SearchQuery

def page_forum(request):
    canonical = request.GET.get('p')
    page = get_object_or_404(Page, canonical=canonical)
    return render(request, 'forum.html', context={"page": page})

def page_room(request):
    canonical = request.GET.get('p')
    page = get_object_or_404(Page, canonical=canonical)
    return render(request, 'room.html', context={"page": page})

@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def page_star(request):
    page_id = request.POST.get('id')
    action = request.POST.get('action')
    if page_id and action:
        try:
            page = Page.objects.get(id=page_id)
            if action == 'star':
                page.users_star.add(request.user)
            else:
                page.users_star.remove(request.user)
            return JsonResponse({'status': '200'})
        except Page.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})
