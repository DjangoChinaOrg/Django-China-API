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
    Serializer for User model used for details
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
        Return the number of posts whose author is this user
        """
        return obj.post_set.count()

    def get_reply_count(self, obj):
        """
        Return the number of replies whose author is this user
        """
        return obj.reply_comments.count()


class UserRegistrationSerializer(RegisterSerializer):
    """
    Inherit from the default serializer in rest_auth, added nickname field
    """
    nickname = serializers.CharField(max_length=50)

    def validate_nickname(self, nickname):
        """
        Validate nickname, it can't be empty or duplicated
        """
        nickname = get_adapter().clean_email(nickname)
        if User.objects.filter(nickname=nickname).exists():
            # TODO: add support for locale
            raise serializers.ValidationError(
                _("已存在一位使用该昵称的用户。")
            )
        return nickname

    def get_cleaned_data(self):
        """
        Override the ancestor's get_cleaned_data method to include [nickname]
        """
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'nickname': self.validated_data.get('nickname', ''),
        }

    def save(self, request):
        """
        Override the ancestor's save method to save [nickname]
        Also save the IP address as the value of [ip_joined]
        """
        # The client's IP address is private
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.nickname = self.cleaned_data.get('nickname')
        ip = get_ip_address_from_request(request)
        if ip:
            user.ip_joined = ip
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
