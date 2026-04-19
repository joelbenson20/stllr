from django.contrib import admin
from .models import Comment, CommentVote

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'page', 'created']
    list_filter = ['created']

admin.site.register(CommentVote)
