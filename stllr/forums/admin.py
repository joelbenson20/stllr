from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content', 'created']
    search_fields = ['author__username', 'content']
    readonly_fields = ['created']
    list_filter = ['created']