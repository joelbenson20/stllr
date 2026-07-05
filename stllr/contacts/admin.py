from django.contrib import admin
from .models import ContactRelation


@admin.register(ContactRelation)
class ContactRelationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created')
    list_filter = ('status',)
    search_fields = ('from_user__username', 'to_user__username')
