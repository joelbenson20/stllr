from django.urls import path
from . import views

app_name = 'extension'

urlpatterns = [
    path('', views.extension, name='extension'),
    path('forum/', views.forum, name='forum'),
    path('relay/', views.relay, name='relay'),
    path('similar/', views.similar, name='similar'),
    path('csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]