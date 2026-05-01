from django.contrib import admin
from .models import Comment, CommentStar

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'created']
    search_fields = ['user__username', 'content']
    readonly_fields = ['created']
    list_filter = ['created']

@admin.register(CommentStar)
class PageStarAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'created']
    readonly_fields = ['created',]
    ordering = ['-created']

