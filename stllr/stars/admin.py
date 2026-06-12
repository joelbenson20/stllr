from django.contrib import admin
from .models import Star


@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ('user', 'object_ct', 'object_id', 'created')
    readonly_fields = ('created',)
    ordering = ['-created']
