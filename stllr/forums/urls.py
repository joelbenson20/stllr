# Done by Claude, requires review
from django.urls import path
from . import views

app_name = 'forums'

urlpatterns = [
    path('<int:page_id>/', views.forum, name='forum'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/toggle-star/', views.toggle_star, name='toggle_star'),
    path('post/<int:post_id>/remove/', views.remove_post, name='remove_post'),
    path('post/removed/', views.remove_post_success, name='remove_post_success'),
    path('markdownify/', views.markdownify, name='markdownify'),
]