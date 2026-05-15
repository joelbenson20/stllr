from .models import Contact

def notifications(request):

    if request.user.is_authenticated:
        pending_requests_count = Contact.objects.filter(
            to_user=request.user,
            status=Contact.Status.PENDING
        ).count()
        return {
             'notifications': {
                  'pending_requests': pending_requests_count
            }
        }
    return {
        'notifications': {
            'pending_requests': 0
        }
    }