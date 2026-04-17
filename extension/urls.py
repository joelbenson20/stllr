from django.urls import path
from . import views

app_name = 'extension'

urlpatterns = [
    path('', views.extension, name='extension'),
    path('csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('page_float/', views.page_float, name='float_webpage'),
]