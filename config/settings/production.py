from .common import *
import environ

ALLOWED_HOSTS = ['.dj-china.org', 'localhost', '127.0.0.1', '0.0.0.0']

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True),
    SOCIAL_LOGIN_GITHUB_CALLBACK_URL=(str, 'http://127.0.0.1:8000/social-auth/github/loginsuccess')
)

environ.Env.read_env()
DEBUG = env('DEBUG')  # default False
SECRET_KEY = env('SECRET_KEY')

# sentry dsn
RAVEN_CONFIG = {
    'dsn': env('SENTRY_DSN'),
}

# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
#
# sentry_sdk.init(
#     dsn=env('SENTRY_DSN'),
#     integrations=[DjangoIntegration()]
# )

# GitHub 登录
SOCIAL_LOGIN_GITHUB_CALLBACK_URL = env('SOCIAL_LOGIN_GITHUB_CALLBACK_URL')

# mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('MYSQL_NAME'),
        'USER': env('MYSQL_USER'),
        'PASSWORD': env('MYSQL_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'autocommit': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'TEST': {
            'NAME': 'django_test',
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        }
    }
}

# 邮件配置，使用腾讯云企业邮箱
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_LOCALTIME = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = 'Django中文社区 <%s>' % EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
