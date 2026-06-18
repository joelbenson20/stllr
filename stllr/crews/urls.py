from django.urls import path
from . import views

app_name = 'crews'

urlpatterns = [
    path('', views.crews, name='crews'),
    path('create/', views.create_crew, name='create_crew'),
    path('<str:handle>/edit/', views.edit_crew, name='edit_crew'),
    path('<str:handle>/', views.crew_beacons, name='crew_detail'),
    path('<str:handle>/stars/', views.crew_stars, name='crew_stars'),
    path('<str:handle>/mentions/', views.crew_mentions, name='crew_mentions'),
    path('<str:handle>/members/', views.crew_members, name='crew_members'),
    path('<str:handle>/members/find/', views.find_members, name='find_members'),
    path('find/', views.find_crews, name='find_crews'),
    path('<str:handle>/join/', views.join_crew, name='join_crew'),
    path('<str:handle>/leave/', views.leave_crew, name='leave_crew'),
    path('<str:handle>/invite/<str:username>/', views.send_invite, name='send_invite'),
    path('<str:handle>/invite/<str:username>/cancel/', views.cancel_invite, name='cancel_invite'),
    path('<str:handle>/accept/', views.accept_invite, name='accept_invite'),
    path('<str:handle>/decline/', views.decline_invite, name='decline_invite'),
    path('<str:handle>/members/<str:username>/admit/', views.admit_member, name='admit_member'),
    path('<str:handle>/members/<str:username>/remove/', views.remove_member, name='remove_member'),
    path('<str:handle>/members/<str:username>/deny/', views.deny_member, name='deny_member'),
    path('<str:handle>/members/<str:username>/set-admin/', views.set_admin, name='set_admin'),
    path('<str:handle>/members/<str:username>/unset-admin/', views.unset_admin, name='unset_admin'),
    path('<str:handle>/members/<str:username>/set-owner/', views.set_owner, name='set_owner'),
    path('<str:handle>/delete/', views.delete_crew, name='delete_crew'),
]