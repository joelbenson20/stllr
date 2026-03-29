from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.api_index, name='api_index'),
    path('vote/webpage/', views.webpage_vote, name='api_webpage_vote'),
]