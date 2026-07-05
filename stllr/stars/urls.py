from django.urls import path
from . import views

app_name = 'stars'

urlpatterns = [
    path('toggle/', views.toggle_star, name='toggle_star'),
]
