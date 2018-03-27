from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from replies.models import Reply


class PublicManager(models.Manager):
    def get_queryset(self):
        return super(PublicManager, self).get_queryset().filter(hidden=False).order_by('-created_time')


class Post(models.Model):
    title = models.CharField("标题", max_length=255)
    body = models.TextField("正文", blank=True)
    views = models.PositiveIntegerField("浏览量", default=0, editable=False)
    created_time = models.DateTimeField("创建时间", auto_now_add=True)
    modified_time = models.DateTimeField("修改时间", auto_now=True)
    pinned = models.BooleanField("置顶", default=False)
    highlighted = models.BooleanField("加精", default=False)
    hidden = models.BooleanField("隐藏", default=False)
    tags = models.ManyToManyField('tags.Tag', verbose_name="标签")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="作者")
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
