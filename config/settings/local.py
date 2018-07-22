from .common import *

ALLOWED_HOSTS = ['*']

SECRET_KEY = 't3l=1)%^^ftao(2_@p^j_$ordrl4rg4-0z1w@^gvvi64balvbx'

# 开发环境下发送的邮件将显示在终端
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'dev.sqlite3'),
    }
}
