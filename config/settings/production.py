from .common import *

DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost ', '.dj-china.org']
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
