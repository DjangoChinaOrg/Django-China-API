from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    目前通知共有 3 种：
    1. 帖子被回复，帖子作者收到通知，通知模型各字段含义为：
        recipient：帖子作者
        actor：回复者
        target：帖子
        action_object：新回复
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

    def update(self, instance, validated_data):
        instance.read()
        return instance

    class Meta:
        model = Notification
        fields = "__all__"
