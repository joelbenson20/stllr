from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('csrf-token/', views.csrf_token, name='csrf-token'),
    path('ws-ticket/', views.ws_ticket, name='ws-ticket'),
    path('markdownify/', views.markdownify, name='markdownify'),
]