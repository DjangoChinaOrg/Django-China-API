import os

from .common import *

DEBUG = True
ALLOWED_HOSTS = ['*']

SECRET_KEY = 't3l=1)%^^ftao(2_@p^j_$ordrl4rg4-0z1w@^gvvi64balvbx'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# envs
MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
MYSQL_DB_NAME = os.getenv('MYSQL_MYSQL_DB_NAME', 'django')
MYSQL_DB_USER = os.getenv('MYSQL_MYSQL_DB_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '19960202')

# database
DATABASES['default'].update(
    {'HOST': MYSQL_HOST,
     'NAME': MYSQL_DB_NAME,
     'USER': MYSQL_DB_USER,
     'PASSWORD': MYSQL_PASSWORD,
     })
