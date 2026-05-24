from django.urls import path
from . import views

app_name = 'forums'

urlpatterns = [
    path('', views.forum, name='forum'),
    path('post/remove/<int:post_id>/', views.remove_post, name='remove_post'),
    path('post/remove/success', views.remove_post_success, name='remove_post_success')
]