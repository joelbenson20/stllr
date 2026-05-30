from users.models import Mute
from comms.models import Notification

def notifications(request):

    if request.user.is_authenticated:
        # Done by Claude, requires review
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
        contacts_list = sorted(
            request.user.get_contacts().select_related('profile'),
            key=lambda u: u.username.lower()
        )
        return {'contacts_list': contacts_list}
    return {'contacts_list': []}

# Done by Claude, requires review
def contacts_statuses(request):
    if request.user.is_authenticated:
        from users.models import Action
        contact_users = request.user.get_contacts()
        actions = (
            Action.objects
            .filter(actor__in=contact_users, removed=False)
            .select_related('actor', 'actor__profile', 'object_ct')
            .order_by('actor_id', '-created')
        )
        seen = set()
        result = []
        for action in actions:
            if action.actor_id not in seen:
                seen.add(action.actor_id)
                result.append(action)
        result.sort(key=lambda a: a.created, reverse=True)
        return {'contacts_statuses': result}
    return {'contacts_statuses': []}

# Done by Claude, requires review
def muted_users(request):
    if request.user.is_authenticated:
        return {
            'muted_user_ids': set(Mute.objects.filter(muter=request.user).values_list('muted_id', flat=True))
        }
    return {'muted_user_ids': set()}