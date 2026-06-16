from django.urls import path
from . import views

app_name = 'crews'

urlpatterns = [
    path('', views.crews, name='crews'),
    path('find/', views.find_crews, name='find_crews'),
    path('create/', views.create_crew, name='create_crew'),
    path('<str:handle>/', views.crew_detail, name='crew_detail'),
    path('<str:handle>/stars/', views.crew_stars, name='crew_stars'),
    path('<str:handle>/edit/', views.edit_crew, name='edit_crew'),
    path('<str:handle>/invite-members/', views.invite_members, name='invite_members'),
    path('<str:handle>/invite/<str:username>/', views.send_invite, name='send_invite'),
    path('<str:handle>/join/', views.join_crew, name='join_crew'),
    path('<str:handle>/leave/', views.leave_crew, name='leave_crew'),
    path('<str:handle>/accept/', views.accept_invite, name='accept_invite'),
    path('<str:handle>/decline/', views.decline_invite, name='decline_invite'),
    path('<str:handle>/delete/', views.delete_crew, name='delete_crew'),
    path('<str:handle>/members/<str:username>/remove/', views.remove_member, name='remove_member'),
    path('<str:handle>/members/<str:username>/set-admin/', views.set_admin, name='set_admin'),
    path('<str:handle>/members/<str:username>/unset-admin/', views.unset_admin, name='unset_admin'),
]