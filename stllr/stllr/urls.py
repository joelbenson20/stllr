from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from users import views as user_views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('comms/', user_views.comms, name='comms'),
    path('users/', include('users.urls')),
    path('forum/', include('forums.urls')),
    path('room/', include('rooms.urls')),
    path('extension/', include('extension.urls', namespace='extension')),
    path('api/', include('api.urls', namespace='api')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )