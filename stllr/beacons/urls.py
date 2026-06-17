from django.urls import path
from . import views

app_name = 'beacons'

urlpatterns = [
    path('', views.beacons, name='beacons'),
    path('feed/', views.feed, name='feed'),
    path('create/', views.create_beacon, name='create_beacon'),
    path('delete/', views.delete_beacon, name='delete_beacon'),
    path('status/', views.beacon_status, name='beacon_status'),
]
