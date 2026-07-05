from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from pages.models import Page
from forums.models import Post
from .notifications import notify
from .models import Notification

User = get_user_model()


@login_required
@require_POST
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def share_object(request):
    object_type = request.POST.get('object_type')
    object_id = request.POST.get('object_id')
    contact_id = request.POST.get('contact_id')

    if not (object_type and object_id and contact_id):
        return JsonResponse({'status': 404}, status=404)

    try:
        recipient = User.objects.get(id=contact_id)
    except User.DoesNotExist:
        return JsonResponse({'status': 400}, status=400)

    if recipient not in request.user.get_contacts():
        return JsonResponse({'status': 403}, status=403)

    if object_type == 'page':
        try:
            obj = Page.objects.get(id=object_id)
            event = Notification.Event.PAGE_SHARED
        except Page.DoesNotExist:
            return JsonResponse({'status': 404}, status=404)
    elif object_type == 'post':
        try:
            obj = Post.objects.get(id=object_id)
            event = Notification.Event.POST_SHARED
        except Post.DoesNotExist:
            return JsonResponse({'status': 404}, status=404)
    else:
        return JsonResponse({'status': 400}, status=400)

    notify(recipient=recipient, event=event, object=obj, actor=request.user)
    return JsonResponse({'status': 200}, status=200)
