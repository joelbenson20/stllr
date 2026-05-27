from .models import Contact, Mute

def notifications(request):

    if request.user.is_authenticated:
        pending_requests = Contact.objects.filter(
            to_user=request.user,
            status=Contact.Status.PENDING
        ).select_related('from_user')
        return {
            'notifications': {
                'pending_requests': pending_requests,
            }
        }
    return {
        'notifications': {
            'pending_requests': [],
        }
    }

# Done by Claude, requires review
def contacts(request):
    if request.user.is_authenticated:
        from django.db.models import Q
        accepted = Contact.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user),
            status=Contact.Status.ACCEPTED
        ).select_related('from_user', 'to_user', 'from_user__profile', 'to_user__profile')
        contacts_list = []
        for contact in accepted:
            other = contact.to_user if contact.from_user == request.user else contact.from_user
            contacts_list.append({'user': other, 'contact': contact})
        contacts_list.sort(key=lambda x: x['user'].username.lower())
        return {'contacts_list': contacts_list}
    return {'contacts_list': []}

# Done by Claude, requires review
def muted_users(request):
    if request.user.is_authenticated:
        return {
            'muted_user_ids': set(Mute.objects.filter(muter=request.user).values_list('muted_id', flat=True))
        }
    return {'muted_user_ids': set()}