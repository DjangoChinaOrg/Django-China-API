from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from replies.api.serializers import TreeReplySerializer
from tags.serializers import TagSerializer

from .models import Post


class PostSerializer(serializers.HyperlinkedModelSerializer):
    """
    帖子序列化器，用于显示帖子列表，帖子详情
    以及帖子创建、编辑
    """
    # TODO: 等待userserializer的定义，返回更相信的author信息
    author = serializers.ReadOnlyField(source='author.username')

    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        read_only_fields = (
            'id',
            'content_type',
            'url',
            'views',
            'created_time',
            'modified_time',
            'pinned',
            'highlighted',
            'replies',
            'reply_count',
            'participants_count',
        )
        fields = (
            'id',
            'content_type',
            'url',
            'title',
            'body',
            'views',
            'created_time',
            'modified_time',
            'pinned',
            'highlighted',
            'tags',
            'author',
            'reply_count',
            'participants_count',
            'replies',
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

    def get_reply_count(self, value):
        """
        返回帖子的回复数量
        """
        return value.replies.count()

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
