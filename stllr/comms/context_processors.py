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
        from django.db.models import Q
        pending = list(
            ContactRelation.objects
            .filter(status=ContactRelation.Status.PENDING)
            .filter(Q(to_user=request.user) | Q(from_user=request.user))
            .select_related('from_user', 'from_user__profile', 'to_user', 'to_user__profile')
        )
        requests_received = [r for r in pending if r.to_user == request.user]
        requests_sent = [r for r in pending if r.from_user == request.user]
        return {'contacts_list': contacts_list, 'requests_received': requests_received, 'requests_sent': requests_sent}
    return {'contacts_list': [], 'requests_received': [], 'requests_sent': []}

def crews(request):
    if request.user.is_authenticated:
        from crews.models import Membership
        all_crews = list(request.user.get_crews())
        pending = list(
            Membership.objects.filter(
                user=request.user,
                status__in=[Membership.Status.INVITED, Membership.Status.REQUESTED],
            ).select_related('crew')
        )
        return {
            'crews_list': all_crews,
            'memberships_invited': [m for m in pending if m.status == Membership.Status.INVITED],
            'memberships_requested': [m for m in pending if m.status == Membership.Status.REQUESTED],
        }
    return {'crews_list': [], 'memberships_invited': [], 'memberships_requested': []}


# TODO: Remove muted_users functionality for now.
def muted_users(request):
    if request.user.is_authenticated:
        return {
            'muted_user_ids': set(Mute.objects.filter(muter=request.user).values_list('muted_id', flat=True))
        }
    return {'muted_user_ids': set()}