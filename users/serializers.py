from ipware import get_client_ip
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from django.utils.translation import ugettext_lazy as _
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from .models import User
from .utils import get_ip_address_from_request


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    用户详细信息的序列器
    """
    post_count = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        read_only_fields = (
            'id',
            'username',
            'nickname',
            'date_joined',
            'ip_joined',
            'last_login_ip',
            'is_superuser',
            'is_staff',
        )
        fields = (
            'id',
            'username',
            'nickname',
            'date_joined',
            'ip_joined',
            'last_login_ip',
            'is_superuser',
            'is_staff',
            'post_count',
            'reply_count',
        )

    def get_post_count(self, obj):
        """
        返回用户提交的帖子数量
        """
        return obj.post_set.count()

    def get_reply_count(self, obj):
        """
        返回用户提交的回复数量
        """
        return obj.reply_comments.count()


class UserRegistrationSerializer(RegisterSerializer):
    """
    继承至rest_auth的默认序列器，增加了昵称
    """

    def save(self, request):
        """
        改写父类的save方法，自动将username存入到nickname域内
        同时检测并存入用户的注册IP地址
        """
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.nickname = self.cleaned_data.get('username')
        ip = get_ip_address_from_request(request)
        if ip:
            user.ip_joined = ip
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
