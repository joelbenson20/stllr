from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('<int:page_id>/', views.room, name='room'),
]
