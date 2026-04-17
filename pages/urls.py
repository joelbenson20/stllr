from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.index, name='index'),
    path('tag/<slug:tag_slug>/', views.index, name='index_by_tag'),
    path('page/', views.page_detail, name='detail'),
    path('page/get_or_create/', views.page_get_or_create, name='get_or_create'),
    path('page/vote/', views.page_vote, name='vote'),
]