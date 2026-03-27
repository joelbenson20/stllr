from django.contrib import admin
from .models import WebpageVote, CommentVote

# Register your models here.
admin.site.register(WebpageVote)
admin.site.register(CommentVote)
