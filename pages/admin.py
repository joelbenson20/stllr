from django.contrib import admin
from .models import Page, PageVote

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['canonical', 'title', 'type',]
    list_filter = ['type', 'tags', 'site_name']
    search_fields = ['canonical', 'title', 'site_name']
    ordering = ['canonical']
    show_facets = admin.ShowFacets.ALWAYS

admin.site.register(PageVote)