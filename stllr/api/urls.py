from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('csrf-token/', views.csrf_token),
    path('ws-ticket/', views.ws_ticket),
    path('markdownify/', views.markdownify),
    path('create/comment/', views.create_comment),
    path('star/page/', views.star_page),
    path('star/comment/', views.star_comment),
]