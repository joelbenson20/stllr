from django.contrib import admin
from .models import PageReport

@admin.register(PageReport)
class PageReportAdmin(admin.ModelAdmin):
    list_display = ['policy', 'page', 'status', 'created_at', 'reviewed_at']
    list_filter= ['status', 'policy']
    ordering = ['created_at']
