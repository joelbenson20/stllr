from django.contrib import admin
from .models import Beacon


@admin.register(Beacon)
class BeaconAdmin(admin.ModelAdmin):
    list_display = ('user', 'crew', 'page', 'created')
    list_filter = ('crew',)
    search_fields = ('user__username', 'crew__handle', 'page__url')
    raw_id_fields = ('user', 'crew', 'page')
