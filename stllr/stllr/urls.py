from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('policies/<str:policy>/', views.policy, name='policy'),
    path('forum/', include('forums.urls')),
    path('room/', include('rooms.urls')),
    path('extension/', include('extension.urls', namespace='extension')),
    path('api/', include('api.urls', namespace='api')),
    path('sentry-debug/', trigger_error)
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )