from django.urls import path
from . import views

urlpatterns = [
    path('vote/webpage/<int:webpage_id>/', views.webpage_vote, name='api_webpage_vote'),
]