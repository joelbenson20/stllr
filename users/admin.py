from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Comment, CommentVote, WebpageVote

# Register your models here.
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(WebpageVote)
admin.site.register(CommentVote)
