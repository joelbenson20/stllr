from users.models import Mute
from comms.models import Notification

# TODO: Move each context processor to its own app.

def notifications(request):

    if request.user.is_authenticated:
        all_notifications = list(
            Notification.objects
            .filter(recipient=request.user)
            .prefetch_related('notification_actors__actor')
        )
        unread = [n for n in all_notifications if not n.read]
        return {
            'notifications': {
                'all': all_notifications,
                'unread': unread,
            }
        }
    return {
        'notifications': {
            'all': [],
            'unread': [],
        }
    }

def contacts(request):
    if request.user.is_authenticated:
        from contacts.models import ContactRelation
        contacts_list = sorted(
            request.user.get_contacts().select_related('profile'),
            key=lambda u: u.username.lower()
        )
        contact_requests = list(
            ContactRelation.objects
            .filter(to_user=request.user, status=ContactRelation.Status.PENDING)
            .select_related('from_user', 'from_user__profile')
        )
        return {'contacts_list': contacts_list, 'contact_requests': contact_requests}
    return {'contacts_list': [], 'contact_requests': []}

def crews(request):
    if request.user.is_authenticated:
        return {'crews_list': request.user.get_crews()}
    return {'crews_list': []}

def muted_users(request):
    if request.user.is_authenticated:
        return {
            'muted_user_ids': set(Mute.objects.filter(muter=request.user).values_list('muted_id', flat=True))
        }
    return {'muted_user_ids': set()}