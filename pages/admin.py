from django.contrib import admin
from .models import Page, PageStar, Domain

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['canonical', 'title', 'type',]
    list_filter = ['type', 'tags', 'domain']
    search_fields = ['canonical', 'title']
    ordering = ['canonical']
    show_facets = admin.ShowFacets.ALWAYS

admin.site.register(PageStar)
admin.site.register(Domain)