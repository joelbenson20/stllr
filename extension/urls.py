from django.urls import path
from . import views

app_name = 'extension'

urlpatterns = [
    path('csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('extension/', views.extension, name='extension'),
    path('float/webpage/', views.float_webpage, name='float_webpage'),
]