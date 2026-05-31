from django.urls import path
from . import views

urlpatterns = [
    # Done by Claude, requires review
    path('<int:page_id>/', views.room, name='room'),
]
