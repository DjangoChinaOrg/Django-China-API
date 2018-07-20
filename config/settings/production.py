import os

from .common import *

DEBUG = False
ALLOWED_HOSTS = ['*']

SECRET_KEY = ''

# envs
MYSQL_HOST = os.getenv('MYSQL_PASSWORD')
MYSQL_DB_NAME = os.getenv('MYSQL_MYSQL_DB_NAME')
MYSQL_DB_USER = os.getenv('MYSQL_MYSQL_DB_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

# database
DATABASES['default'].update(
    {'HOST': MYSQL_HOST,
     'NAME': MYSQL_DB_NAME,
     'USER': MYSQL_DB_USER,
     'PASSWORD': MYSQL_PASSWORD,
     })
