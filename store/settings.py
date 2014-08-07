"""
Django settings for store project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from __future__ import absolute_import
import os
import djcelery

from .celery import app as celery_app

djcelery.setup_loader()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8^h)b(&q39twcf_^ukd3(@1von9o9)#390henl-bt%)fc-=(&*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.comments',
    'south',
    'debug_toolbar',
    'dbsettings',
    'djcelery',
    'webstore',
    'paypal.standard.ipn',
    'social.apps.django_app.default',
    'notifications'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'store.middlewares.UserMiddleware',
)
AUTHENTICATION_BACKENDS = (
    #'social.backends.facebook.Facebook2OAuth2',
    #'social.backends.twitter.TwitterOAuth',
    'webstore.authentication_backend.FacebookBackend',
    'webstore.authentication_backend.TwitterBackend',
    'webstore.authentication_backend.ProxyUserBackend',
)

AUTH_PROFILE_MODULE = 'webstore.UserProfile'

FACEBOOK_APP_ID                 = '708254132555429'
FACEBOOK_API_SECRET             = '63a80eb14a82774b7552ad8c26b19bbb'
SOCIAL_AUTH_FACEBOOK_KEY        = '708254132555429'
SOCIAL_AUTH_FACEBOOK_SECRET     = '63a80eb14a82774b7552ad8c26b19bbb'
SOCIAL_AUTH_TWITTER_KEY         = 'IMRGG9fR76Z1aR6nMCBZz4qOe'
SOCIAL_AUTH_TWITTER_SECRET      = 'QQUfZiIMatwdSFA0dP3hHDb1XK660Qa72ZCPAh4bYdzU77PSUO'

#SOCIAL_AUTH_USER_MODEL = 'webstore.models.ProxyUser'

SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_birthday', 'user_hometown', 'user_location',
                              'user_interests', 'user_photos']
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'webstore.pipeline.user_details'
)


SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 3600,
    }
}

ROOT_URLCONF = 'store.urls'

WSGI_APPLICATION = 'store.wsgi.application'

PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = "crisan_mariusvlad-facilitator@yahoo.com"
PAYPAL_IDENTITY_TOKEN = "-hSqcphpCSGu6n7HkOqokYH1ssfhGFVKejomDWrxYMNGMI3V26w_FCGRXt0"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'store',
        'USER': 'marius',
        'PASSWORD': 'marius',
        'HOST': 'localhost',                               
        'PORT': '',                      
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "social.apps.django_app.context_processors.backends",
    "social.apps.django_app.context_processors.login_redirect",
    "webstore.context_processors.load_sidebar_cart",
    "webstore.context_processors.load_sidebar_search",
    "webstore.context_processors.load_categories",
)

SITE_ID = 1

#celery
celery_app.conf.update(
    BROKER_URL = 'redis://localhost:6379/0',
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0',
)
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'crisan.mariusvlad@gmail.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

COMMENTS_APP = 'webstore'
