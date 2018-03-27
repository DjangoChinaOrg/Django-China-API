from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        exclude = ('hidden',)

    # 验证tag field
    def validate_tags(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("最多可以选择3个标签")
        return value
