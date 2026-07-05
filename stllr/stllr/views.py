from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from pages.models import Page

def home(request):
    return render(request, 'home.html', {
        'sort': request.GET.get('sort', 'firmament'),
    })

def explore(request):
    return render(request, 'explore.html', {
        'query': request.GET.get('query', ''),
        'sort': request.GET.get('sort', 'firmament'),
    })

@login_required
def comms(request):
    from comms.models import Notification
    response = render(request, 'comms.html')
    Notification.objects.filter(recipient=request.user, read=False).update(read=True)
    return response

@login_required
def pins(request):
    pinned_pages = Page.objects.filter(pins__user=request.user).order_by('-pins__created')
    return render(request, 'pins.html', {'pages': pinned_pages})

def policy(request, policy):
    if (policy == 'privacy-policy'):
        return render(request, 'policies/generated-privacy-policy.html')
    elif (policy == 'user-agreement'):
        return render(request, 'policies/user-agreement.html')
    else:
        raise Http404(f"Policy {policy} was not found.")