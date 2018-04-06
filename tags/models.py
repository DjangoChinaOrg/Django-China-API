from django.conf import settings
from django.db import models


class Tag(models.Model):
    created_time = models.DateTimeField("创建时间", auto_now_add=True)
    name = models.CharField("标签名", max_length=100, unique=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="创建者")

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"

    def __str__(self):
        return self.name
