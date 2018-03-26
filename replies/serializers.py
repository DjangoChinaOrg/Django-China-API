from rest_framework import serializers

from .models import Reply


class ReplyCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ('content_type', 'object_pk', 'site',
                  'comment', 'submit_date', 'ip_address',
                  'parent',)
        extra_kwargs = {
            'submit_date': {'required': False, 'allow_null': True},

            # 似乎以下设置没有生效
            'ip_address': {'required': False, 'allow_null': True},
            'site': {'default': 1},
        }