from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.feed_view, name='index'),
    path('forum/', views.page_forum, name='forum'),
    path('relay/', views.page_relay, name='relay'),
    path('page/star/', views.page_star, name='star'),
]