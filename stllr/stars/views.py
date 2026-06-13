from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import Star


@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def toggle_star(request):
    model_name = request.POST.get('object_ct')
    object_id = request.POST.get('object_id')
    action = request.POST.get('action')

    if model_name not in ('page', 'post'):
        return JsonResponse({'status': 400}, status=400)

    object_ct = get_object_or_404(ContentType, model=model_name)
    get_object_or_404(object_ct.model_class(), pk=object_id)

    if action == 'star':
        _, created = Star.objects.get_or_create(user=request.user, object_ct=object_ct, object_id=object_id)
        if not created:
            return JsonResponse({'status': 409}, status=409)
    elif action == 'unstar':
        star = get_object_or_404(Star, user=request.user, object_ct=object_ct, object_id=object_id)
        star.delete()
    else:
        return JsonResponse({'status': 400}, status=400)

    return JsonResponse({'status': 200}, status=200)
