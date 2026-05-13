from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('forum/', views.page_forum, name='forum'),
    path('room/', views.page_room, name='room'),
    path('page/star/', views.page_star, name='star'),
]