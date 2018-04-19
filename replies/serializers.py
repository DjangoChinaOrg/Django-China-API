from actstream.models import Follow
from rest_framework import serializers

from replies.models import Reply


class FlatReplySerializer(serializers.ModelSerializer):
    """
    返回一个扁平化的按发表时间倒序排序的 reply 列表，无视其层级关系。
    适合用在 user 详情页面的个人回复列表中。
    """
    # TODO: 应该返回被回复帖子的 hyperlink，用户点击帖子标题后就跳转到帖子页面的回复处
    # TODO: 应该返父回复用户的 hyperlink，用户点击昵称后跳转到该用户的详情页
    # TODO：等帖子和用户的 API 确定后再修改
    post_title = serializers.SerializerMethodField()
    parent_user = serializers.SerializerMethodField()

    # TODO: 统一到 user 中，等待 UserSerializer 的定义
    # 获取用户头像报 Unicode 编码错误
    # user_mugshot = serializers.SerializerMethodField()
    user_nickname = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            # 'user_mugshot',
            'user_nickname',
            'post_title',
            'submit_date',
            'comment',
            'parent_user',
            'like_count',
        )

    def get_post_title(self, obj):
        return obj.content_object.title

    def get_parent_user(self, obj):
        if obj.parent:
            return obj.parent.user.nickname
        return None

    def get_user_mugshot(self, obj):
        return obj.user.mugshot

    def get_user_nickname(self, obj):
        return obj.user.nickname

    def get_like_count(self, obj):
        return Follow.objects.for_object(obj, flag='like').count()


class ReplyCreationSerializer(serializers.ModelSerializer):
    """
    仅用于 reply 的创建
    """

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
        )
        read_only_fields = (
            'submit_date',
            'ip_address',
            'is_public',
            'is_removed',
        )


class TreeRepliesSerializer(serializers.ModelSerializer):
    """
    返回两层的 reply，第一层为根 reply，第二层为这个 reply 的所有子孙 reply。
    这个 Serializer 适合用于帖子详情页的 reply 列表。
    """
    descendants = FlatReplySerializer(many=True)
    num_descendants = serializers.SerializerMethodField()

    # TODO: 统一到 user 中，等待 UserSerializer 的定义
    # user_mugshot = serializers.SerializerMethodField()
    user_nickname = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            'content_type',
            'object_pk',
            # 'user_mugshot',
            'user_nickname',
            'comment',
            'submit_date',
            'like_count',
            'num_descendants',
            'descendants',
        )

    def get_num_descendants(self, obj):
        return obj.descendants().count()

    def get_user_mugshot(self, obj):
        return obj.user.mugshot

    def get_user_nickname(self, obj):
        return obj.user.nickname

    def get_like_count(self, obj):
        return Follow.objects.for_object(obj, flag='like').count()


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
