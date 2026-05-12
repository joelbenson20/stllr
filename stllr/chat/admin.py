from django.contrib import admin
from chat.models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sent_on', 'user', 'page', 'content']
    list_filter = ['sent_on']
    search_fields = ['content']
    raw_id_fields = ['user', 'page']
