import random
from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required
from pages.models import Page

def home(request):
    request.session['feed_seed'] = random.random()
    return render(request, 'home.html')

def explore(request):
    request.session['feed_seed'] = random.random()
    return render(request, 'explore.html', {
        'query': request.GET.get('query', ''),
        'sort': request.GET.get('sort', 'firmament'),
    })

@login_required
def contacts(request):
    return render(request, 'contacts.html')

@login_required
def comms(request):
    from comms.models import Notification
    Notification.objects.filter(recipient=request.user, read=False).update(read=True)
    return render(request, 'comms.html')

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