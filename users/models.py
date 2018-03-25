import os

from django.db import models
from django.contrib.auth.models import AbstractUser


def user_mugshot_path(instance, filename):
    return os.path.join('mugshots', instance.username, filename)


class User(AbstractUser):
    last_login_ip = models.GenericIPAddressField("最近一次登陆IP", unpack_ipv4=True, blank=True, null=True)
    ip_joined = models.GenericIPAddressField("注册IP", unpack_ipv4=True, blank=True, null=True)

    nickname = models.CharField("昵称", max_length=50, unique=True)
    mugshot = models.ImageField("头像", upload_to=user_mugshot_path)

    def __str__(self):
        return self.username
