
from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.index, name='index'),
    path('page/<int:pk>/', views.page_forum, name='page_forum'),
    path('float/', views.post_float, name='post_float'),
]