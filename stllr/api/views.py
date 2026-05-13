from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.middleware.csrf import get_token
from forums.templatetags.safe_markdown import safe_markdown_filter
import secrets
from django.core.cache import cache
from django.http import JsonResponse

@login_required
def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

@login_required
def ws_ticket(request):
    token = secrets.token_urlsafe(32)
    cache.set(f'ws_ticket:{token}', request.user.id, timeout=30)
    return JsonResponse({'ticket': token})

@login_required
@require_POST
def markdownify(request):
    content = request.POST.get('content', '')
    response = {
        'status': '200',
        'markdown': safe_markdown_filter(content),
    }
    return JsonResponse(response)
