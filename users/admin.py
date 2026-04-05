from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, WebpageVote

# Register your models here.
admin.site.register(User)
admin.site.register(WebpageVote)
