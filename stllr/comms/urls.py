# Done by Claude, requires review
from django.urls import path
from . import views

app_name = 'comms'

urlpatterns = [
    path('share/', views.share_object, name='share_object'),
]
