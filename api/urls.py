from django.urls import path
from . import views

urlpatterns = [
    path('csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('extension/', views.extension, name='extension'),
    path('vote/webpage/', views.webpage_vote, name='api_webpage_vote'),
]