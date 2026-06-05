from django.contrib import admin
from .models import PageReport, PostReport

@admin.register(PageReport)
class PageReportAdmin(admin.ModelAdmin):
    fields = ['reporter', 'page', 'policy', 'justification', 'status', 'reviewed_at']
    list_display = ['policy', 'page', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'policy']
    ordering = ['created_at']

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    fields = ['reporter', 'post', 'policy', 'justification', 'status', 'reviewed_at']
    list_display = ['policy', 'post', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'policy']
    ordering = ['created_at']

