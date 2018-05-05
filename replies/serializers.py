from actstream.models import Follow
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from rest_framework import serializers

from posts.models import Post
from replies.models import Reply


class FlatReplySerializer(serializers.ModelSerializer):
    """
    返回一个扁平化的按发表时间倒序排序的 reply 列表，无视其层级关系。
    适合用在 user 详情页面的个人回复列表中。
    """
    post = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    parent_user = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            'id',
            'user',
            'parent_user',
            'post',
            'submit_date',
            'comment',
            'like_count',
            'is_liked',
        )

    def get_post(self, obj):
        post = obj.content_object
        return {
            'id': post.id,
            'title': post.title,
        }

    def get_user(self, obj):
        user = obj.user
        request = self.context.get('request')
        url = user.mugshot.url
        return {
            'id': user.id,
            'mugshot': request.build_absolute_uri(url) if request else url,
            'nickname': user.nickname,
        }

    def get_parent_user(self, obj):
        parent = obj.parent
        if not parent:
            return None
        user = parent.user
        request = self.context.get('request')
        url = user.mugshot.url
        return {
            'id': user.id,
            'mugshot': request.build_absolute_uri(url) if request else url,
            'nickname': user.nickname,
        }

    def get_is_liked(self, obj):
        request = self.context.get('request')
        return Follow.objects.is_following(request.user, obj, flag='like')


class ReplyCreationSerializer(serializers.ModelSerializer):
    """
    仅用于 reply 的创建
    """
    parent_user = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            'id',
            'object_pk',
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
            'id',
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
        request = self.context.get('request')
        url = user.mugshot.url
        return {
            'id': user.id,
            'mugshot': request.build_absolute_uri(url) if request else url,
            'nickname': user.nickname,
        }

    def get_user(self, obj):
        user = obj.user
        request = self.context.get('request')
        url = user.mugshot.url
        return {
            'id': user.id,
            'mugshot': request.build_absolute_uri(url) if request else url,
            'nickname': user.nickname,
        }

    def create(self, validated_data):
        post_id = validated_data.get('object_pk')
        post_ctype = ContentType.objects.get_for_model(
            Post.objects.get(id=int(post_id))
        )
        site = Site.objects.get_current()
        validated_data['content_type'] = post_ctype
        validated_data['site'] = site
        return super(ReplyCreationSerializer, self).create(validated_data)


class TreeRepliesSerializer(serializers.ModelSerializer):
    """
    返回两层的 reply，第一层为根 reply，第二层为这个 reply 的所有子孙 reply。
    这个 Serializer 适合用于帖子详情页的 reply 列表。
    """
    descendants = FlatReplySerializer(many=True)
    user = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            'id',
            'content_type',
            'object_pk',
            'comment',
            'submit_date',
            'like_count',
            'user',
            'descendants',
            'descendants_count',
            'is_liked'
        )

    def get_is_liked(self, obj):
        request = self.context.get('request')
        return Follow.objects.is_following(request.user, obj, flag='like')

    def get_user(self, obj):
        user = obj.user
        request = self.context.get('request')
        url = user.mugshot.url
        return {
            'id': user.id,
            'mugshot': request.build_absolute_uri(url) if request else url,
            'nickname': user.nickname,
        }


class FollowSerializer(serializers.ModelSerializer):
    """
    用于记录回复的点赞信息
    """

    class Meta:
        model = Follow
        fields = (
            'id',
            'user',
            'content_type',
            'object_id',
            'flag',
            'started',
        )
        read_only_fields = (
            'id',
            'user',
            'content_type',
            'object_id',
            'flag',
            'started',
        )

    def create(self, validated_data):
        reply_id = validated_data.get('object_pk')
        reply_ctype = ContentType.objects.get_for_model(
            Reply.objects.get(id=int(reply_id))
        )
        validated_data['content_type'] = reply_ctype
        return super(FollowSerializer, self).create(validated_data)
