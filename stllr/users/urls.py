from django.urls import path, include
from . import views

urlpatterns = [
    path('search/', views.search_users, name='search_users'),
    path('action/<int:action_id>/remove/', views.remove_action, name='remove_action'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/edit/', views.edit, name='edit'),
    path('<str:username>/add/', views.send_request, name='send_request'),
    path('<str:username>/accept/', views.accept_request, name='accept_request'),
    path('<str:username>/decline/', views.decline_request, name='decline_request'),
    path('<str:username>/remove/', views.remove_contact, name='remove_contact'),
    path('<str:username>/mute/', views.mute_user, name='mute_user'),
]