from django.contrib import admin
from .models import Crew, Membership


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    fields = ('user', 'role', 'status', 'created', 'joined')
    readonly_fields = ('created', 'joined')


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ('handle', 'name', 'creator', 'created')
    search_fields = ('handle', 'name')
    readonly_fields = ('created',)
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'crew', 'role', 'status', 'created', 'joined')
    list_filter = ('status', 'role')
    search_fields = ('user__username', 'crew__handle')
    readonly_fields = ('created', 'joined')
