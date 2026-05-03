from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import JsonResponse
from comments.templatetags.safe_markdown import safe_markdown_filter
from comments.forms import CommentForm

@login_required
@require_POST
def markdownify(request):
    content = request.POST.get('content', '')
    response = {
        'status': '200',
        'markdown': safe_markdown_filter(content),
    }
    return JsonResponse(response)
