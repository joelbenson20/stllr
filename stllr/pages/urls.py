from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('bookmark/<int:page_id>/', views.toggle_bookmark, name='toggle_bookmark'),
]
