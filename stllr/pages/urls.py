from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.feed_view, name='index'),
    path('page/', views.page_detail, name='detail'),
    path('page/star/', views.page_star, name='star'),
]