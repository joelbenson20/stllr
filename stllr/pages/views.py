# Done by Claude, requires review
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Page, PagePin


@login_required
def toggle_pin(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    action = request.GET.get('action', 'pin')
    if action == 'pin':
        PagePin.objects.get_or_create(page=page, user=request.user)
    else:
        PagePin.objects.filter(page=page, user=request.user).delete()
    return redirect('pins')
