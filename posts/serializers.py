from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from replies.serializers import TreeRepliesSerializer
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
            'created_time',
            'modified_time',
            'latest_reply_time',
            'pinned',
            'highlighted',
            'tags',
            'author',
            'reply_count',
        )

    def get_author(self, obj):
        author = obj.author
        return {
            'id': author.id,
            'mugshot': author.mugshot.url,
            'nickname': author.nickname,
        }

    def get_reply_count(self, value):
        """
        返回帖子的回复数量
        """
        return value.replies.count()

    def get_latest_reply_time(self, value):
        """
        返回最后一次评论的时间，
        如果没有评论，返回null
        """
        replies = value.replies.all().order_by('-submit_date')
        if replies:
            return replies[0].submit_date
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
        return {
            'id': author.id,
            'mugshot': author.mugshot.url,
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
            'created_time',
            'modified_time',
            'body',
            'tags',
            'reply_count',
            'participants_count',
        )

    def get_content_type(self, value):
        """
        帖子的content_type
        """
        content_type = ContentType.objects.get_for_model(value)
        return content_type.id

    def get_replies(self, value):
        """
        返回帖子下的回复
        """
        replies = value.replies.filter(parent__isnull=True)
        serializer = TreeRepliesSerializer(replies, many=True)
        return serializer.data

    def get_participants_count(self, value):
        """
        返回评论参与者数量
        """
        user_list = []
        replies = value.replies.all()
        for reply in replies:
            if reply.user not in user_list:
                user_list.append(reply.user)
        return len(user_list)
