from django.contrib import admin
from .models import Prompt


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ('title', 'page', 'model', 'created')
    list_filter = ('model',)
    search_fields = ('title', 'prompt', 'page__canonical')
    readonly_fields = ('created',)
