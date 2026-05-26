from pathlib import Path
from celery.schedules import crontab
from decouple import config
from django.contrib.messages import constants as messages


SITE_ID = 1
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = config('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = [
    'stllr.io',
    'www.stllr.io',
    '107.170.16.225',
    'localhost',
    '127.0.0.1'
]

CORS_ALLOWED_ORIGINS = [
    'chrome-extension://polpgpcagljhejdbajfbjgdchdlnfepk',
    'chrome-extension://mlilkidmlfonjgccanoodpmbfjflggla',
    'chrome-extension://hmpgjgepcimfdojfbffhaedmkndomfml',
]

CSRF_TRUSTED_ORIGINS = [
    'https://stllr.io',
    'https://www.stllr.io',
    'http://107.170.16.225',
    'https://107.170.16.225',
    'http://localhost',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://127.0.0.1:8000',
    'chrome-extension://polpgpcagljhejdbajfbjgdchdlnfepk',
    'chrome-extension://mlilkidmlfonjgccanoodpmbfjflggla',
    'chrome-extension://hmpgjgepcimfdojfbffhaedmkndomfml',
]

INSTALLED_APPS = [
    'daphne',
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.postgres',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'stllr',
    'pages.apps.PagesConfig',
    'forums.apps.ForumsConfig',
    'rooms.apps.RoomsConfig',
    'governance.apps.GovernanceConfig',
    'extension.apps.ExtensionConfig',
    'api.apps.APIConfig',
    'corsheaders',
    'storages',
    'taggit',
    'easy_thumbnails',
    'markdown_deux',
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'stllr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'stllr.wsgi.application'

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'email'
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Done by Claude, requires review
ACCOUNT_ADAPTER = 'users.adapters.AccountAdapter'
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[stllr] '
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_METHODS = {'username', 'email'}  # Done by Claude, requires review
SOCIALACCOUNT_LOGIN_ON_GET = True
# Done by Claude, requires review
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_FORMS = {'signup': 'users.forms.SocialSignupForm'}

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT', cast=int)
    }
}

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config('REDIS_URL'),
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [config('REDIS_URL')],
        },
    },
}

CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE  # reuse Django's TIME_ZONE
CELERY_TASK_TIME_LIMIT = 5 * 60  # hard kill after 5 min

CELERY_BEAT_SCHEDULE = {
    "delete-old-page-stars": {
        "task": "pages.delete_old_page_stars",
        "schedule": crontab(),
    },
    "update-page-brightnesses": {
        "task": "pages.update_page_brightnesses",
        "schedule": crontab(),
    },
    "update-brightness-index": {
        "task": "pages.update_brightness_index",
        "schedule": crontab(),
    },
    "delete-old-post-stars": {
        "task": "forum.delete_old_post_stars",
        "schedule": crontab(),
    },
    "update-post-brightnesses": {
        "task": "forum.update_post_brightnesses",
        "schedule": crontab(),
    },
}

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'