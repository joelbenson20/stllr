from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('markdownify/', views.markdownify, name='markdownify'),
]