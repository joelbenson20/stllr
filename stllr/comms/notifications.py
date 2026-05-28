from django.contrib.contenttypes.models import ContentType
from .models import Notification, NotificationActor

def notify(recipient, event, object, actor):
    if recipient == actor:
        return
    object_ct = ContentType.objects.get_for_model(object)
    notification, _ = Notification.objects.get_or_create(
        recipient=recipient,
        event=event,
        object_ct=object_ct,
        object_id=object.pk
    )
    NotificationActor.objects.get_or_create(notification=notification, actor=actor)
    notification.actor_count = notification.actors.count()
    notification.read = False
    notification.save(update_fields=['actor_count', 'read'])
