from .common import *

DEBUG = True

SECRET_KEY = 't3l=1)%^^ftao(2_@p^j_$ordrl4rg4-0z1w@^gvvi64balvbx'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'apps.home',
]
