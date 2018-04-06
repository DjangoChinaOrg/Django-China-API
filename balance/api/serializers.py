from rest_framework import serializers

from ..models import Record


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = (
            'reward_type',
            'coin_type',
            'amount',
            'description',
            'user',
        )
        read_only_fields = (
            'reward_type',
            'coin_type',
            'amount',
            'description',
            'user',
        )
