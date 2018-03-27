from rest_framework import serializers

from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Tag
        fields = '__all__'
