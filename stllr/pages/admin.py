from django.contrib import admin
from .models import Page, Domain

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['canonical', 'title', 'brightness']
    list_filter = ['domain']
    search_fields = ['canonical', 'title']
    ordering = ['canonical']
    show_facets = admin.ShowFacets.ALWAYS

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'name', 'category']
    search_fields = ['name', 'site_name']
    ordering = ['name']