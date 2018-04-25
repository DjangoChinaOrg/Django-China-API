from actstream.models import Follow
from rest_framework import serializers

from replies.models import Reply


class FlatReplySerializer(serializers.ModelSerializer):
    """
    返回一个扁平化的按发表时间倒序排序的 reply 列表，无视其层级关系。
    适合用在 user 详情页面的个人回复列表中。
    """
    post = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    parent_user = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            'user',
            'parent_user',
            'post',
            'submit_date',
            'comment',
            'like_count',
        )

    def get_post(self, obj):
        post = obj.content_object
        return {
            'id': post.id,
            'title': post.title,
        }

    def get_user(self, obj):
        user = obj.user
        return {
            'id': user.id,
            'nickname': user.nickname,
            'mugshot': user.mugshot.url,
        }

    def get_parent_user(self, obj):
        parent = obj.parent
        if not parent:
            return None
        user = parent.user
        return {
            'id': user.id,
            'nickname': user.nickname,
            'mugshot': user.mugshot.url,
        }


class ReplyCreationSerializer(serializers.ModelSerializer):
    """
    仅用于 reply 的创建
    """
    parent_user = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            'content_type',
            'object_pk',
            'site',
            'comment',
            'parent',
            'submit_date',
            'ip_address',
            'is_public',
            'is_removed',
            'user',
            'parent_user',
        )
        read_only_fields = (
            'submit_date',
            'ip_address',
            'is_public',
            'is_removed',
        )

    def get_parent_user(self, obj):
        parent = obj.parent
        if not parent:
            return None
        user = parent.user
        return {
            'id': user.id,
            'nickname': user.nickname,
            'mugshot': user.mugshot.url,
        }

    def get_user(self, obj):
        user = obj.user
        return {
            'id': user.id,
            'nickname': user.nickname,
            'mugshot': user.mugshot.url,
        }


class TreeRepliesSerializer(serializers.ModelSerializer):
    """
    返回两层的 reply，第一层为根 reply，第二层为这个 reply 的所有子孙 reply。
    这个 Serializer 适合用于帖子详情页的 reply 列表。
    """
    descendants = FlatReplySerializer(many=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            'content_type',
            'object_pk',
            'comment',
            'submit_date',
            'like_count',
            'user',
            'descendants',
            'descendants_count',
        )

    def get_user(self, obj):
        user = obj.user
        return {
            'id': user.id,
            'nickname': user.nickname,
            'mugshot': user.mugshot.url,
        }


class FollowSerializer(serializers.ModelSerializer):
    """
    用于记录回复的点赞信息
    """

    class Meta:
        model = Follow
        fields = (
            'user',
            'content_type',
            'object_id',
            'flag',
            'started',
        )
        read_only_fields = (
            'user',
            'content_type',
            'object_id',
            'flag',
            'started',
        )
