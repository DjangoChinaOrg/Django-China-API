from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from .models import Post
from tags.serializers import TagSerializer
from replies.api.serializers import TreeReplySerializer


class IndexPostListSerializer(serializers.HyperlinkedModelSerializer):
    """
    首页帖子列表序列化器
    """
    # TODO: 等待userserializer的定义，返回更详细的author信息
    author = serializers.SerializerMethodField(read_only=True)

    reply_count = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True)
    latest_reply_time = serializers.SerializerMethodField(read_only=True)

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

    def get_author(self, value):
        data = {}
        data['id'] = value.author.id
        try:
            data['mugshot'] = value.author.mugshot.url
        except ValueError:
            data['mugshot'] = None
        data['nickname'] = value.author.nickname
        return data

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
    # TODO: 返回user_url 需要实现了user-deail
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'url',
            'title',
            'author',
        )

    def get_author(self, value):
        data = {}
        data['id'] = value.author.id
        data['mugshot'] = value.author.mugshot.url
        return data


class PostDetailSerializer(IndexPostListSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    replies = serializers.SerializerMethodField(read_only=True)
    participants_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'author',
            'views',
            'created_time',
            'modified_time',
            'body',
            'tags',
            'reply_count',
            'participants_count',
            'replies'
        )

    def get_content_type(self, value):
        """

        """
        content_type = ContentType.objects.get_for_model(value)
        return content_type.id

    def get_replies(self, value):
        """
        返回帖子下的回复
        """
        replies = value.replies.filter(parent__isnull=True)
        serializer = TreeReplySerializer(replies, many=True)
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
