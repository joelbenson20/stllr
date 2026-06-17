from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    path('<str:username>/', views.profile_posts, name='profile'),
    path('<str:username>/stars/', views.profile_stars, name='profile_stars'),
    path('<str:username>/replies/', views.profile_replies, name='profile_replies'),
    path('<str:username>/mentions/', views.profile_mentions, name='profile_mentions'),
    path('<str:username>/crews/', views.profile_crews, name='profile_crews'),
    path('<str:username>/edit/', views.edit, name='edit'),
    path('<str:username>/mute/', views.mute_user, name='mute_user'),
]