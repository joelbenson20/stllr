from django.urls import path
from . import views

app_name = 'extension'

urlpatterns = [
    path('', views.extension, name='extension'),
]