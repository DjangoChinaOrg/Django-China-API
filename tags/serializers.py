from rest_framework import serializers

from .models import Tag


class TagSerializer(serializers.HyperlinkedModelSerializer ):

    class Meta:
        model = Tag
        fields = (
            'id',
            'url',
            'name',
        )
