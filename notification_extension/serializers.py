from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    unread = serializers.BooleanField(default=True)
    deleted = serializers.BooleanField(default=False)

    def update(self, instance, validated_data):
        instance.read()
        return instance

    class Meta:
        model = Notification
        fields = "__all__"
