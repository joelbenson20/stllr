from django.urls import path
from . import views

app_name = 'crews'

urlpatterns = [
    path('', views.crews, name='crews'),
    path('create/', views.create_crew, name='create_crew'),
    path('<str:handle>/', views.crew_detail, name='crew_detail'),
    path('<str:handle>/edit/', views.edit_crew, name='edit_crew'),
]