from datetime import timedelta
from django.utils import timezone
from celery import shared_task

BROADCAST_RETENTION = timedelta(days=90)

@shared_task(name='rooms.delete_old_broadcasts')
def delete_old_broadcasts():
    from .models import Broadcast
    cutoff = timezone.now() - BROADCAST_RETENTION
    for broadcast in Broadcast.objects.filter(created__lt=cutoff):
        broadcast.delete()
    return