import os

import dj_database_url

# Docker build secrets
from .keyconfig import Database

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = Database.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#DEBUG = False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
  'channels',
  'dal', # autocomplete, before admin in case used in admin
  'dal_select2',
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'accounts',
  'chat',
  'importer',
  'files',
  'spectra_search',
  'spectra',
  'django_tables2',
  'django_filters',
  'bootstrap4',
  'jquery',
  'django_extensions',
  'rest_framework',
  'ncbitaxonomy',
  'django.contrib.postgres' # To use the search lookup, 'django.contrib.postgres'
                            # must be in your INSTALLED_APPS.
  #'ajaxuploader',
]

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  #'whitenoise.middleware.WhiteNoiseMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mdb.urls'

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'libs', 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
      'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
      ],
    },
  },
]

WSGI_APPLICATION = 'mdb.wsgi.application'
ASGI_APPLICATION = 'mdb.routing.application'
# ~ ASGI_APPLICATION = 'mdb.asgi.application'

CHANNEL_LAYERS = {
  "default": {
    "BACKEND": "channels.layers.InMemoryChannelLayer"
  },
}

DATABASES = {
  "default": {
#       'ENGINE': 'django.db.backends.postgresql_psycopg2',
    "ENGINE": "django.db.backends.postgresql",
    "NAME": Database.NAME,
    "USER": Database.USER,
    "PASSWORD": Database.PASSWORD,
    "HOST": Database.HOST,
    "PORT": Database.PORT,
  }
}

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATICFILES_DIRS = [
  os.path.join(BASE_DIR, "libs", "static"),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Authentication URLS
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login'

# Authentication User Model
AUTH_USER_MODEL = 'accounts.User'

# 500MB - 429916160
# 2000MB - 1719664640
#MAX_UPLOAD_SIZE = 1719664640

