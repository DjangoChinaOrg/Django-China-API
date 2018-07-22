from .common import *

DEBUG = False
ALLOWED_HOSTS = ['.dj-china.org', 'localhost', '127.0.0.1', '0.0.0.0']
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# envs
MYSQL_HOST = os.getenv('MYSQL_PASSWORD')
MYSQL_DB_NAME = os.getenv('MYSQL_MYSQL_DB_NAME')
MYSQL_DB_USER = os.getenv('MYSQL_MYSQL_DB_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

# sentry dsn
RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_DSN', ''),
}

# 0: production
# 1: local test
local_test = os.environ.get('LOCAL_TEST', 0)

if local_test:
    DEBUG = True
    # sqlite3
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'dev.sqlite3'),
        }
    }
else:
    # database
    DATABASES['default'].update(
        {'HOST': MYSQL_HOST,
         'NAME': MYSQL_DB_NAME,
         'USER': MYSQL_DB_USER,
         'PASSWORD': MYSQL_PASSWORD,
         })

# 邮件配置，使用腾讯云企业邮箱
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_LOCALTIME = True
EMAIL_HOST_USER = 'master@dj-china.org'
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD', 'fallback_value')

# Default email address to use for various automated correspondence from the site manager(s).
DEFAULT_FROM_EMAIL = 'Django中文社区 <%s>' % EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
