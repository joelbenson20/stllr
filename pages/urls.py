from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.page_feed, name='index'),
    path('tag/<slug:tag_slug>/', views.page_feed, name='index_by_tag'),
    path('page/', views.page_detail, name='detail'),
    path('page/star/', views.page_star, name='star'),
]