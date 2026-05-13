from django.contrib import admin
from rooms.models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['created', 'user', 'page', 'content']
    list_filter = ['created']
    search_fields = ['content']
    raw_id_fields = ['user', 'page']
