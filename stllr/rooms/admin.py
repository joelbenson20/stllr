from django.contrib import admin
from rooms.models import Broadcast

@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ['created', 'user', 'page', 'content']
    list_filter = ['created']
    search_fields = ['content']
    raw_id_fields = ['user', 'page']
