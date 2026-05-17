from django.contrib import admin
from .models import Post, PostStar

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'created']
    search_fields = ['user__username', 'content']
    readonly_fields = ['created']
    list_filter = ['created']

@admin.register(PostStar)
class PageStarAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created']
    readonly_fields = ['created',]
    ordering = ['-created']