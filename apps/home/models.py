from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=100)  # 文章标题

    content = models.TextField()  # 文章内容

    created_time = models.DateTimeField()  # 文章创建时间

    excerpt = models.TextField(max_length=200, blank=True)  # 文章摘要

    author = models.ForeignKey(User)

    views_num = models.PositiveIntegerField(default=0)  # 阅读数量

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
    title = models.CharField(max_length=100, blank=False, null=False, unique=True)  # 进度条名称

    progress = models.IntegerField(blank=False, null=False)  # 进度条进程

    remarks = models.CharField(max_length=100)  # 进度条备注

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "进度条"
        verbose_name_plural = verbose_name
