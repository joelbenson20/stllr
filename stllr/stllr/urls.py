from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('explore/', views.explore, name='explore'),
    path('contacts/', include('contacts.urls', namespace='contacts')),
    path('comms/', views.comms, name='comms'),  # TODO: Move all these tabs into their respective apps
    path('pins', views.pins, name='pins'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls', namespace='users')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('stars/', include('stars.urls', namespace='stars')),
    path('forums/', include('forums.urls', namespace='forums')),
    path('rooms/', include('rooms.urls', namespace='rooms')),
    path('crews/', include('crews.urls', namespace='crews')),
    path('comms/', include('comms.urls', namespace='comms')),
    path('oversight/', include('oversight.urls', namespace='oversight')),
    path('policies/<str:policy>/', views.policy, name='policy'), # TODO: Move policies urls and views into oversight
    path('extension/', include('extension.urls', namespace='extension')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )