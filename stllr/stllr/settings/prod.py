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
    ('Stllr Admin', config('EMAIL_HOST_USER'))
]

# TODO: remove dummy backend and uncomment SMTP config once Gmail is working
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')