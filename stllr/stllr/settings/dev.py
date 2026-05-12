from .base import *

ASGI_APPLICATION = 'stllr.asgi.application'

DEBUG = True
THUMBNAIL_DEBUG = False

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static/dev'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/dev'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'