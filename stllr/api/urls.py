from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('markdownify/', views.markdownify, name='markdownify'),
    path('create/post/', views.create_post, name='create_post'),
    path('star/page/', views.star_page, name='star_page'),
    path('pin/page/', views.pin_page, name='pin_page'),
    path('star/post/', views.star_post, name='star_post'),
    path('count/room/', views.get_room_count, name='get_room_count'),
    path('mute/user/', views.mute_user, name='mute_user'),
    path('search/users/', views.search_users, name='search_users'),
    path('share/', views.share_object, name='share_object'),
]