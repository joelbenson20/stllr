from .base import *

DEBUG = False
THUMBNAIL_DEBUG = False

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static/prod'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/prod'