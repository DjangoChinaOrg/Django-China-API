from rest_framework import serializers
from notifications.models import Notification

from users.serializers import UserSimpleDetailsSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """
    目前通知共有 3 种：
    1. 帖子被评论，帖子作者收到通知，通知模型各字段含义为：
        recipient：帖子作者
        actor：回复者
        target：帖子
        action_object：新评论
        verb: 'reply'

    2. 帖子的回复被其他人回复，即回复别人的回复，被回复者收到通知：
        recipient：被回复者
        actor：回复者
        target：帖子
        action_object：新回复
        verb: 'respond'

    3. 回复被点赞：
        recipient：被赞者
        actor：回复者
        target：被赞的回复
        action_object：被赞的回复所属的帖子
        verb: 'like'
    """
    actor = UserSimpleDetailsSerializer()
    post = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()

    def get_reply(self, obj):
        if obj.verb == 'like':
            reply = obj.target
            return {
                'comment': reply.comment
            }
        elif obj.verb == 'reply':
            reply = obj.action_object
            return {
                'comment': reply.comment
            }
        elif obj.verb == 'respond':
            reply = obj.action_object
            return {
                'comment': reply.comment
            }

    def get_post(self, obj):
        if obj.verb == 'like':
            post = obj.action_object
            return {
                'post_id': post.id,
                'post_title': post.title
            }
        else:
            post = obj.target
            return {
                'post_id': post.id,
                'post_title': post.title
            }

    class Meta:
        model = Notification
        fields = ('id', 'unread', 'actor', 'verb', 'timestamp', 'deleted', 'recipient', 'post', 'reply')
