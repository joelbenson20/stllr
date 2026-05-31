# Done by Claude, requires review
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Page, PageStar, PagePin
from users.models import Action


@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def toggle_star(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    action = request.POST.get('action')
    if action == 'star':
        PageStar.objects.get_or_create(page=page, user=request.user)
        Action.objects.create(actor=request.user, verb=Action.Verb.STARRED, object=page)
    elif action == 'unstar':
        star = PageStar.objects.filter(page=page, user=request.user).first()
        if star:
            star.delete()
    else:
        return JsonResponse({'status': '400'}, status=400)
    return JsonResponse({'status': '200'})


@login_required
@require_POST
def toggle_pin(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    action = request.POST.get('action')
    if action == 'pin':
        PagePin.objects.get_or_create(page=page, user=request.user)
    elif action == 'unpin':
        pin = PagePin.objects.filter(page=page, user=request.user).first()
        if pin:
            pin.delete()
    else:
        return JsonResponse({'status': '400'}, status=400)
    return JsonResponse({'status': '200'})
