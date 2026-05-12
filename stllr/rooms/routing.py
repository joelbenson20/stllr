from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/chat/room/(?P<page_id>\d+)/$',
        consumers.RoomConsumer.as_asgi()
    )
]