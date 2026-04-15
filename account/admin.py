from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, PageVote

admin.site.register(User)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'photo']
    raw_id_fields = ['user']

admin.site.register(PageVote)
