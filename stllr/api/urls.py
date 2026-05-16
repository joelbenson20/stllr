from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('markdownify/', views.markdownify, name='markdownify'),
    path('create/comment/', views.create_comment, name='create_comment'),
    path('star/page/', views.star_page, name='star_page'),
    path('star/comment/', views.star_comment, name='star_comment'),
    path('count/room/', views.get_room_count, name='get_room_count'),
]