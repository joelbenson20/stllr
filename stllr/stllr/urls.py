from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('explore/', views.explore, name='explore'),
    path('contacts/', views.contacts, name='contacts'),
    path('comms/', views.comms, name='comms'),
    path('pins', views.pins, name='pins'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('policies/<str:policy>/', views.policy, name='policy'),
    path('forums/', include('forums.urls', namespace='forums')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('rooms/', include('rooms.urls', namespace='rooms')),
    path('extension/', include('extension.urls', namespace='extension')),
    path('comms/', include('comms.urls', namespace='comms')),
    path('oversight/', include('oversight.urls', namespace='oversight')),  # Done by Claude, requires review
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )