import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# defaults
DEFAULT_SECRET_KEY = 'lolinsecure1337lolinsecure1337lolinsecure1337lolinsecure1337lolinsecure1337lolinsecure1337lolinsecure1337lolinsecure1337lolinsecure1337lolinsecure1337'
SECRET_KEY = DEFAULT_SECRET_KEY

DEBUG = True
PAGE_LIVE = True

DOMAIN = "localhost"
ALLOWED_HOSTS = ["*"]

BBB_SECRETS_DIR = os.path.join(BASE_DIR, "_bbb_secrets")
STATIC_ROOT = os.path.join(BASE_DIR, "_static")
MEDIA_ROOT = os.path.join(BASE_DIR, "_media")

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = '/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '_db.sqlite3'),
    }
}

# Application definition
INSTALLED_APPS = [
    'channels',
    'chat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'landingpage',
    'partners',
    'bbb',
    'eventpage',
    'helpers',
    'authstuff',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'authstuff.middleware.NameMiddleware',
]

ROOT_URLCONF = 'voctoconf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'voctoconf.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = 'authstuff.User'
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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
    ('de', 'Deutsch'),
)

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

ASGI_APPLICATION = 'voctoconf.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

try:
    from .local_settings import *
except:
    print("#############")
    print("## WARNING ##")
    print("#############")
    print("")
    print("NO LOCAL CONFIGURATION FOUND")
    print("USING DEV DEFAULTS")
    print("DONT RUN THIS ON THE INTERWEBZ")
    print("")

if not DEBUG and SECRET_KEY == DEFAULT_SECRET_KEY:
    print("LOL NOPE")
    sys.exit(1)
