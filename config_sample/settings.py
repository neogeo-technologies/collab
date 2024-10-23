"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from decouple import config, Csv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default="SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost, 127.0.0.1, 0.0.0.0', cast=Csv())

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default="", cast=Csv())

USE_X_FORWARDED_HOST = config('USE_X_FORWARDED_HOST', default=False, cast=bool)

# Application definition
CORE_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.flatpages',
    'django_admin_listfilter_dropdown',
]
THIRD_PARTY_DJANGO_APPS = config(
    'THIRD_PARTY_DJANGO_APPS', 
    default='rest_framework, rest_framework_gis, django_celery_beat, drf_yasg', 
    cast=Csv()
)
OUR_APPS = config('OUR_APPS', default='geocontrib, api', cast=Csv())
SSO_PLUGIN = config('SSO_PLUGIN', default='', cast=Csv())
INSTALLED_APPS = CORE_APPS + THIRD_PARTY_DJANGO_APPS + OUR_APPS + SSO_PLUGIN

CORE_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
]
SSO_MIDDLEWARE = config('SSO_MIDDLEWARE', default='', cast=Csv())
MIDDLEWARE = CORE_MIDDLEWARE + SSO_MIDDLEWARE

ROOT_URLCONF = 'config.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'geocontrib.context_processors.custom_contexts',
            ],
        },
    },
]
WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config("DB_NAME", default='geocontrib'),
        'USER': config("DB_USER", default='geocontrib'),
        'PASSWORD': config("DB_PWD", default='geocontrib'),
        'HOST': config("DB_HOST", default='geocontrib-db'),
        'PORT': config("DB_PORT", default='5432')
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = config('LANGUAGE_CODE', default='fr-FR')
TIME_ZONE = config("TIME_ZONE", default='Europe/Paris')
USE_I18N = True
USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.auth.backends.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        # declare other parsers before xml to set them as default
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        # accept xml logout request from CAS server as geOrchestra
        'rest_framework_xml.parsers.XMLParser',
    ),
}

# URL prefix
URL_PREFIX = config('URL_PREFIX', default='geocontrib/')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static and media files
STATIC_URL = '/{}static/'.format(URL_PREFIX)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/{}media/'.format(URL_PREFIX)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Extended properties
AUTH_USER_MODEL = 'geocontrib.User'
LOGIN_URL = config("LOGIN_URL", default='geocontrib:login')
LOGIN_REDIRECT_URL = 'geocontrib:index'
LOGOUT_REDIRECT_URL = 'geocontrib:index'
SSO_OGS_SESSION_URL = config('SSO_OGS_SESSION_URL', default='')

# CAS https://djangocas.dev/docs/latest/configuration.html#cas-server-url-required
cas_server_url = config('CAS_SERVER_URL', None)
if cas_server_url:
    CAS_SERVER_URL = cas_server_url
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'django_cas_ng.backends.CASBackend',
    )
    CAS_APPLY_ATTRIBUTES_TO_USER = True

# Configure automated view generation
AUTOMATIC_VIEW_CREATION_MODE = config("AUTOMATIC_VIEW_CREATION_MODE", default='Type')
AUTOMATIC_VIEW_SCHEMA_NAME = config("AUTOMATIC_VIEW_SCHEMA_NAME", default='')

# Configure django admin
LOGOUT_HIDDEN = config("LOGOUT_HIDDEN", default=False, cast=bool)
HIDE_USER_CREATION_BUTTON = config("HIDE_USER_CREATION_BUTTON", default=False, cast=bool)

# Configure frontend
LOG_URL = config("LOG_URL", default=None)
DISABLE_LOGIN_BUTTON = config("DISABLE_LOGIN_BUTTON", default=None)


# Logging properties
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {pathname}, @{lineno} :\n {message} \n',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('LOG_LEVEL', default='WARN'),
            'propagate': True,
        },
        'plugin_georchestra': {
            'handlers': ['console'],
            'level': config('LOG_LEVEL', default='DEBUG'),
            'propagate': True,
        },
    },
}

# E-mail and notification parameters
# EMAIL_BACKEND = config('EMAIL_BACKEND', default="django.core.mail.backends.console.EmailBackend")
# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# EMAIL_PORT = config('EMAIL_PORT', cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# Notification frequency (allowed values: 'never', 'instantly', 'daily', 'weekly')
DEFAULT_SENDING_FREQUENCY = config('DEFAULT_SENDING_FREQUENCY', default='never')

# Custom Contexts: cf 'geocontrib.context_processors.custom_contexts'
APPLICATION_NAME = config('APPLICATION_NAME', default='GéoContrib')
APPLICATION_ABSTRACT = config('APPLICATION_ABSTRACT',
                              default="Application de saisie d'informations géographiques contributive")
LOGO_PATH = config('LOGO_PATH', default=os.path.join(MEDIA_URL, 'logo-neogeo-circle.png'))
FAVICON_PATH = config('FAVICON_PATH', default=os.path.join(MEDIA_URL, 'logo-neogeo-circle.png'))

# Allowed formats for file attachments
IMAGE_FORMAT = config('IMAGE_FORMAT', default='application/pdf,image/png,image/jpeg')

# Max size of file attachments
FILE_MAX_SIZE = config('FILE_MAX_SIZE', default=10000000)

SITE_ID = 1

# Default basemap config (following leaflet syntax)
DEFAULT_BASE_MAP = {
    'SERVICE': 'https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png',
    'OPTIONS': {
        'attribution': '&copy; contributeurs d\'<a href="https://osm.org/copyright">OpenStreetMap</a>',
        'maxZoom': 20
    }
}

# Default project map extent
# France (continental extent)
DEFAULT_MAP_VIEW = {
    'center': [47.0, 1.0],
    'zoom': 4
}

# Hauts-de-France administrative area
# DEFAULT_MAP_VIEW = {
#     'center': [50.00976, 2.8657699],
#     'zoom': 7
# }

# Bourgogne Franche Comté administrative area
# DEFAULT_MAP_VIEW = {
#     'center': [47.5, 5.7],
#     'zoom': 7
# }

# Project duplication settings
PROJECT_COPY_RELATED = {
    'AUTHORIZATION': config('PROJECT_COPY_RELATED_AUTHORIZATION', default=True, cast=bool),
    'BASE_MAP': True,
    'FEATURE': True,
    'FEATURE_TYPE': True,
    'THUMBNAIL': True,
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = config('DATA_UPLOAD_MAX_NUMBER_FIELDS', default=10000)

# 9745 & 9645 don't create temp files with 0o000
FILE_UPLOAD_PERMISSIONS = 0o644

# 10683
BASE_URL = config('BASE_URL', default='http://localhost:8000')

# CELERY/REDIS confs (#10665)
REDIS_HOST = config('REDIS_HOST', default='localhost')

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=f'redis://{ REDIS_HOST }:6379')

CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=f'redis://{ REDIS_HOST }:6379')

CELERY_ACCEPT_CONTENT = config('CELERY_ACCEPT_CONTENT', default='application/json', cast=Csv())

CELERY_TASK_SERIALIZER = config('CELERY_TASK_SERIALIZER', default='json')

CELERY_RESULT_SERIALIZER = config('CELERY_RESULT_SERIALIZER', default='json')

MAGIC_IS_AVAILABLE = config('MAGIC_IS_AVAILABLE', default=True, cast=bool)  # File image validation (@seb / install IdeoBFC)

# Import features from datasud
IDGO_URL = config('IDGO_URL', default='https://idgo.dev.neogeo.local/api/resources_vector_by_user/')
MAPSERVER_URL = config('MAPSERVER_URL', default='https://mapserver.dev.neogeo.local/maps/')
IDGO_VERIFY_CERTIFICATE = config('IDGO_VERIFY_CERTIFICATE', default=False)
IDGO_LOGIN = config('IDGO_LOGIN', default='geocontrib')
IDGO_PASSWORD = config('IDGO_PASSWORD', default='CHANGE_ME')

SESSION_COOKIE_NAME='geocontrib-session-id'

# Required to avoid error in swagger
SWAGGER_SETTINGS = {
    'LOGIN_URL': '/login/',
}