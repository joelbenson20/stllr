
from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.webpage_detail, name='webpage_detail'),
]