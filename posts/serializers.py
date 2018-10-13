from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from rest_framework import serializers

from tags.serializers import TagSerializer
from utils.mixins import EagerLoaderMixin
from .models import Post, Reply


class IndexPostListSerializer(serializers.HyperlinkedModelSerializer, EagerLoaderMixin):
    """
    首页帖子列表序列化器
    """
    author = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    latest_reply_time = serializers.SerializerMethodField()

    SELECT_RELATED_FIELDS = ['author']
    PREFETCH_RELATED_FIELDS = [
        'tags',
        Prefetch('replies', queryset=Reply.objects.order_by('-submit_date'))
    ]

    class Meta:
        model = Post
        fields = (
            'id',
            'url',
            'title',
            'views',
            'created',
            'modified',
            'latest_reply_time',
            'pinned',
            'highlighted',
            'tags',
            'author',
            'reply_count',
        )

    def get_author(self, obj):
        author = obj.author
        request = self.context.get('request')
        url = author.mugshot.url
        thumbnail_url = author.mugshot_thumbnail.url
        return {
            'id': author.id,
            'mugshot': request.build_absolute_uri(url) if request else url,
            'mugshot_url': request.build_absolute_uri(thumbnail_url) if request else url,
            'nickname': author.nickname,
        }

    def get_reply_count(self, obj):
        """
        返回帖子的回复数量
        """
        return obj.replies.count()

    def get_latest_reply_time(self, obj):
        """
        返回最后一次评论的时间，
        如果没有评论，返回null
        """
        replies = obj.replies.all()
        if replies:
            return replies[0].submit_date
        else:
            return None


class PopularPostSerializer(serializers.HyperlinkedModelSerializer, EagerLoaderMixin):
    """
    热门帖子序列化器
    """
    author = serializers.SerializerMethodField()

    SELECT_RELATED_FIELDS = ['author']

    class Meta:
        model = Post
        fields = (
            'id',
            'url',
            'title',
            'author',
        )

    def get_author(self, obj):
        author = obj.author
        request = self.context.get('request')
        url = author.mugshot.url
        thumbnail_url = author.mugshot_thumbnail.url
        return {
            'id': author.id,
            'mugshot': request.build_absolute_uri(url) if request else url,
            'mugshot_url': request.build_absolute_uri(thumbnail_url) if request else url,
            'nickname': author.nickname,
        }


class PostDetailSerializer(IndexPostListSerializer):
    """
    用来显示帖子详情，已经用来创建、修改帖子的序列化器
    """
    author = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'content_type',
            'title',
            'author',
            'views',
            'created',
            'modified',
            'body',
            'tags',
            'reply_count',
            'participants_count',
        )

    def get_content_type(self, obj):
        """
        帖子的content_type
        """
        content_type = ContentType.objects.get_for_model(obj)
        return content_type.id

    def get_participants_count(self, obj):
        """
        返回评论参与者数量
        """
        return obj.replies.values_list('user', flat=True).distinct().count()
