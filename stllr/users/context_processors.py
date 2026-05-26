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
def muted_users(request):
    if request.user.is_authenticated:
        return {
            'muted_user_ids': set(Mute.objects.filter(muter=request.user).values_list('muted_id', flat=True))
        }
    return {'muted_user_ids': set()}