import os

from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.db import models

from .mugshot import Avatar
from .utils import get_ip_address_from_request


def user_mugshot_path(instance, filename):
    return os.path.join('mugshots', instance.username, filename)


class User(AbstractUser):
    """
    用户模型定义
    """
    last_login_ip = models.GenericIPAddressField("最近一次登陆IP", unpack_ipv4=True, blank=True, null=True)
    ip_joined = models.GenericIPAddressField("注册IP", unpack_ipv4=True, blank=True, null=True)

    nickname = models.CharField("昵称", max_length=50, unique=True)
    mugshot = models.ImageField("头像", upload_to=user_mugshot_path)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.mugshot:
            avatar = Avatar(rows=10, columns=10)
            image_byte_array = avatar.get_image(
                string=self.username,
                width=480,
                height=480,
                pad=10
            )
            self.mugshot.save('default_mugshot.png', ContentFile(image_byte_array), save=False)
        if not self.pk and not self.nickname:
            # 自动将username存入到nickname域内
            self.nickname = self.username
        super(User, self).save(*args, **kwargs)


def update_last_login_ip(sender, user, request, **kwargs):
    """
    更新用户最后一次登陆的IP地址
    """
    ip = get_ip_address_from_request(request)
    if ip:
        user.last_login_ip = ip
        user.save()


user_logged_in.connect(update_last_login_ip)
