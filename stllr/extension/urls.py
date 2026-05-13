from django.urls import path
from . import views

app_name = 'extension'

urlpatterns = [
    path('', views.extension, name='extension'),
    path('forum/', views.forum, name='forum'),
    path('room/', views.room, name='room'),
    path('similar/', views.similar, name='similar'),
]