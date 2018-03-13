from django.db import models

from django_comments.abstracts import CommentAbstractModel
from mptt.models import MPTTModel, TreeForeignKey


class Reply(MPTTModel, CommentAbstractModel):
    parent = TreeForeignKey('self', null=True, blank=True,
                            verbose_name="上级回复", related_name='children',
                            on_delete=models.SET_NULL)

    class Meta(CommentAbstractModel.Meta):
        verbose_name = "回复"
        verbose_name_plural = "回复"
