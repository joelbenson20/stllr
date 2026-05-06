from .base import *

DEBUG = False
THUMBNAIL_DEBUG = False

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static/prod'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/prod'

ADMINS = [
    ('Stllr Admin', config('ADMIN_EMAIL'))
]

EMAIL_BACKEND = 'anymail.backends.resend.EmailBackend'
ANYMAIL = {'RESEND_API_KEY': config('RESEND_API_KEY')}
DEFAULT_FROM_EMAIL = 'admin@stllr.io'