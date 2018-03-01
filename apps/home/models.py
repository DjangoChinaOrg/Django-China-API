import datetime
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name='文章标题')  # 文章标题

    content = models.TextField(verbose_name='文章内容')  # 文章内容

    created_time = models.DateTimeField(verbose_name='创建时间')  # 文章创建时间

    excerpt = models.TextField(max_length=200, blank=True, verbose_name='文章摘要')  # 文章摘要

    author = models.ForeignKey(User,verbose_name='作者')

    views_num = models.PositiveIntegerField(default=0,verbose_name='阅读数量')  # 阅读数量

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('home:post', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def increase_views_num(self):
        self.views_num += 1
        self.save(update_fields=['views_num'])


class ProgressBar(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False, unique=True, verbose_name='进度条名称')  # 进度条名称

    progress = models.IntegerField(blank=False, null=False, verbose_name='进度条进程')  # 进度条进程

    remarks = models.CharField(max_length=100, verbose_name='备注')  # 进度条备注

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "进度条"
        verbose_name_plural = verbose_name


class Support(models.Model):
    CHANNEL_TYPE = (
        (1, "微信"),
        (2, "支付宝"),
    )
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name='捐助人')
    money = models.IntegerField(blank=False, null=False, verbose_name='捐助金额')
    channel = models.IntegerField(choices=CHANNEL_TYPE, blank=False, null=False, verbose_name='捐助渠道')
    date = models.DateField(blank=False, null=False, verbose_name='捐助时间')
    remarks = models.CharField(max_length=100, default='-', verbose_name='备注',blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "捐助"
        verbose_name_plural = verbose_name
