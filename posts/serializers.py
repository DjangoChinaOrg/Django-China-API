from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from tags.serializers import TagSerializer
from .models import Post


class IndexPostListSerializer(serializers.HyperlinkedModelSerializer):
    """
    首页帖子列表序列化器
    """
    author = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    latest_reply_time = serializers.SerializerMethodField()

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
        return {
            'id': author.id,
            'mugshot': request.build_absolute_uri(url) if request else url,
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
        reply_times = obj.replies.values_list('submit_date', flat=True). \
            order_by('-submit_date')
        if reply_times:
            return reply_times[0]
        else:
            return None


class PopularPostSerializer(serializers.HyperlinkedModelSerializer):
    """
    热门帖子序列化器
    """
    author = serializers.SerializerMethodField()

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
        return {
            'id': author.id,
            'mugshot': request.build_absolute_uri(url) if request else url,
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
