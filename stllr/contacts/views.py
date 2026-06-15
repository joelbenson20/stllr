from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from .models import ContactRelation


@login_required
def contacts(request):
    return render(request, 'contacts.html')


@login_required
def find_contacts(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        User = get_user_model()
        users = User.objects.filter(username__icontains=q)[:20]
        relations = {}
        for rel in ContactRelation.objects.filter(
            Q(from_user=request.user, to_user__in=users) |
            Q(to_user=request.user, from_user__in=users)
        ).select_related('from_user', 'to_user'):
            other = rel.to_user if rel.from_user == request.user else rel.from_user
            relations[other.pk] = rel
        for u in users:
            results.append({'user': u, 'relation': relations.get(u.pk)})
    return render(request, 'find_contacts.html', {'q': q, 'results': results})


@login_required
def send_request(request, username):
    to_user = get_object_or_404(get_user_model(), username=username)
    if to_user == request.user:
        return HttpResponseBadRequest()
    contact, _ = ContactRelation.objects.get_or_create(from_user=request.user, to_user=to_user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'contact/status_button.html',
            {'other': to_user, 'contact': contact},
            request=request,
        ))
    return redirect('users:profile', username=username)


@login_required
def accept_request(request, username):
    from_user = get_object_or_404(get_user_model(), username=username)
    contact = get_object_or_404(
        ContactRelation, from_user=from_user, to_user=request.user,
        status=ContactRelation.Status.PENDING
    )
    contact.status = ContactRelation.Status.ACCEPTED
    contact.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'contact/status_button.html',
            {'other': from_user, 'contact': contact},
            request=request,
        ))
    return redirect('users:profile', username=username)


@login_required
def decline_request(request, username):
    other_user = get_object_or_404(get_user_model(), username=username)
    ContactRelation.objects.filter(from_user=request.user, to_user=other_user).delete()
    ContactRelation.objects.filter(from_user=other_user, to_user=request.user).delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'contact/status_button.html',
            {'other': other_user, 'contact': None},
            request=request,
        ))
    return redirect('users:profile', username=request.user.username)


@login_required
def remove_contact(request, username):
    other_user = get_object_or_404(get_user_model(), username=username)
    ContactRelation.objects.filter(from_user=request.user, to_user=other_user).delete()
    ContactRelation.objects.filter(from_user=other_user, to_user=request.user).delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(render_to_string(
            'contact/status_button.html',
            {'other': other_user, 'contact': None},
            request=request,
        ))
    return redirect('users:profile', username=username)
