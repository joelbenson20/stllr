
from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.index, name='index'),
    path('forum/', views.page_forum, name='page_forum'),
    path('page_float/', views.page_float, name='page_float'),
]