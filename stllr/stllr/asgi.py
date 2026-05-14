"""
ASGI config for float project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stllr.settings.dev')

django_asgi_app = get_asgi_application()

WEBSOCKET_ALLOWED_ORIGINS = [
    'http://localhost',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://127.0.0.1:8000',
    'https://stllr.io',
    'https://www.stllr.io',
    'chrome-extension://polpgpcagljhejdbajfbjgdchdlnfepk',
    'chrome-extension://mlilkidmlfonjgccanoodpmbfjflggla',
]

from rooms.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': OriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        WEBSOCKET_ALLOWED_ORIGINS,
    ),
})