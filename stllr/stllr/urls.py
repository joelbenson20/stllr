from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# Done by Claude, requires review
from forums.views import post_detail

urlpatterns = [
    path('', views.home, name='home'),
    path('explore/', views.explore, name='explore'),
    path('contacts/', views.contacts, name='contacts'),
    path('comms/', views.comms, name='comms'),  # Done by Claude, requires review
    path('pins', views.pins, name='pins'),  # Done by Claude, requires review
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('policies/<str:policy>/', views.policy, name='policy'),
    path('forum/', include('forums.urls', namespace='forums')),
    path('post/<int:post_id>/', post_detail, name='post_detail'),  # Done by Claude, requires review
    path('rooms/', include('rooms.urls')),
    path('extension/', include('extension.urls', namespace='extension')),
    path('api/', include('api.urls', namespace='api')),
    path('governance/', include('governance.urls', namespace='governance')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )