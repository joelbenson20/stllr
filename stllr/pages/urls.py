from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('<int:page_id>/toggle-star/', views.toggle_star, name='toggle_star'),
    path('<int:page_id>/toggle-pin/', views.toggle_pin, name='toggle_pin'),
]
