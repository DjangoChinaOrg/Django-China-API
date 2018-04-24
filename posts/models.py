from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from model_utils.models import TimeStampedModel

from replies.models import Reply


class PublicManager(models.Manager):
    def get_queryset(self):
        return super(PublicManager, self).get_queryset().filter(hidden=False).order_by('-created_time')


class Post(TimeStampedModel):
    title = models.CharField("标题", max_length=255)
    body = models.TextField("正文", blank=True)
    views = models.PositiveIntegerField("浏览量", default=0, editable=False)
    pinned = models.BooleanField("置顶", default=False)
    highlighted = models.BooleanField("加精", default=False)
    hidden = models.BooleanField("隐藏", default=False)
    tags = models.ManyToManyField('tags.Tag', verbose_name="标签")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="作者", on_delete=models.CASCADE)
    replies = GenericRelation(Reply, object_id_field='object_pk', content_type_field='content_type',
                              verbose_name="回复")

    objects = models.Manager()
    # 未隐藏的帖子
    public = PublicManager()

    class Meta:
        verbose_name = "帖子"
        verbose_name_plural = "帖子"

    def __str__(self):
        return self.title
