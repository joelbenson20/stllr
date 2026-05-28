from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('pin/<int:page_id>/', views.toggle_pin, name='toggle_pin'),  # Done by Claude, requires review
]
