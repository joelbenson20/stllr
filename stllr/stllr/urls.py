from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('', include('pages.urls', namespace='pages')),
    path('comments/', include('comments.urls', namespace='comments')),
    path('extension/', include('extension.urls', namespace='extension')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )