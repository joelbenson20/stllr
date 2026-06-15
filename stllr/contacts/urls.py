from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.contacts, name='contacts'),
    path('find/', views.find_contacts, name='find_contacts'),
    path('add/<str:username>/', views.send_request, name='send_request'),
    path('accept/<str:username>/', views.accept_request, name='accept_request'),
    path('decline/<str:username>/', views.decline_request, name='decline_request'),
    path('remove/<str:username>/', views.remove_contact, name='remove_contact'),
]
