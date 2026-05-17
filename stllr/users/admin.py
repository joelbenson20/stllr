from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Action

admin.site.register(User)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'background']
    raw_id_fields = ['user']

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ['user', 'verb', 'page']