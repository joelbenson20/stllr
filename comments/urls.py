from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('post/<int:page_id>/', views.post_comment, name='post')
]