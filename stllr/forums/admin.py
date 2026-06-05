from django.contrib import admin
from .models import Post, PostStar

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content', 'created']
    search_fields = ['author__username', 'content']
    readonly_fields = ['created']
    list_filter = ['created']

@admin.register(PostStar) # TODO: change the class name to PostStarAdmin??
class PageStarAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created']
    readonly_fields = ['created',]
    ordering = ['-created']