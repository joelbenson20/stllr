from django.contrib import admin
from .models import Notification, NotificationActor


class NotificationActorInline(admin.TabularInline):
    model = NotificationActor
    extra = 0
    readonly_fields = ('actor', 'created')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'event', 'actor_count', 'read', 'updated')
    list_filter = ('event', 'read')
    readonly_fields = ('recipient', 'event', 'object_ct', 'object_id', 'actor_count', 'created', 'updated')
    inlines = [NotificationActorInline]
