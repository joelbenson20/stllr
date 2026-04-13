from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.index, name='index'),
    path('#/<slug:tag_slug>/', views.index, name='index_by_tag'),
    path('page/', views.page_detail, name='page_detail'),
    path('page_float/', views.page_float, name='page_float'),
]