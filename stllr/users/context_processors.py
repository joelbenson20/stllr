from .models import Contact

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