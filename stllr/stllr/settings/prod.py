import os
from .base import *
import sentry_sdk

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
    ('Stllr Admin', 'admin@stllr.io')
]

EMAIL_BACKEND = 'anymail.backends.resend.EmailBackend'
ANYMAIL = {'RESEND_API_KEY': config('RESEND_API_KEY')}
DEFAULT_FROM_EMAIL = 'noreply@stllr.io'

sentry_sdk.init( #TODO: Make sure logged data does not conflict with the privacy policy.
    dsn="https://5c723cba6d02bc486ffb90cdc646fd0c@o4511436617809920.ingest.us.sentry.io/4511436622856192",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)