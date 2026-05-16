from django.urls import path
from . import views

app_name = 'extension'

urlpatterns = [
    path('', views.extension, name='extension'),
    path('csrf-token/', views.csrf_token),
    path('ws-ticket/', views.ws_ticket),
    path('loading/', views.loading, name='loading'),
    path('restricted/', views.restricted, name='restricted'),
]