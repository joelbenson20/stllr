from django.urls import path
from . import views

app_name = 'crews'

urlpatterns = [
    path('', views.crews, name='crews'),
    path('find/', views.find_crews, name='find_crews'),
    path('create/', views.create_crew, name='create_crew'),
    path('<str:handle>/', views.crew_detail, name='crew_detail'),
    path('<str:handle>/edit/', views.edit_crew, name='edit_crew'),
    path('<str:handle>/invite/<str:username>/', views.send_invite, name='send_invite'),
    path('<str:handle>/join/', views.join_crew, name='join_crew'),
    path('<str:handle>/leave/', views.leave_crew, name='leave_crew'),
    path('<str:handle>/accept/', views.accept_invite, name='accept_invite'),
    path('<str:handle>/decline/', views.decline_invite, name='decline_invite'),
]