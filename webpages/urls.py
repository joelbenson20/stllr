
from django.urls import path
from . import views

app_name = 'webpages'

urlpatterns = [
    path('<int:pk>/', views.detail, name='detail'),
    path('float/', views.post_float, name='post_float'),
]