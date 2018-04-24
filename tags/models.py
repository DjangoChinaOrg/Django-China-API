from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class Tag(TimeStampedModel):
    name = models.CharField("标签名", max_length=100, unique=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="创建者", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"

    def __str__(self):
        return self.name
