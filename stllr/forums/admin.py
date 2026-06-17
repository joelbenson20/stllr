from django.contrib import admin
from .models import Post, Mention


class MentionInline(admin.TabularInline):
    model = Mention
    extra = 0
    readonly_fields = ['user', 'crew']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content', 'created']
    search_fields = ['author__username', 'content']
    readonly_fields = ['created']
    list_filter = ['created']
    inlines = [MentionInline]


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'post', 'user', 'crew']
    search_fields = ['user__username', 'crew__handle', 'post__content']
    list_filter = ['user', 'crew']
    raw_id_fields = ['post', 'user', 'crew']