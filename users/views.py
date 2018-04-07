import math
import random

from allauth.account.views import ConfirmEmailView as AllAuthConfirmEmailView
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from balance.api.permissions import IsCurrentUser, OncePerDay
from balance.api.serializers import BalanceSerializer
from balance.models import Record
from replies.api.serializers import FlatReplySerializer

from .models import User
from .serializers import UserDetailsSerializer


class ConfirmEmailView(AllAuthConfirmEmailView):
    """
    用户点击Email里的激活链接后跳转的视图
    """
    template_name = 'email_confirm.html'

    def post(self, *args, **kwargs):
        response = super(ConfirmEmailView, self).post(*args, **kwargs)
        confirmation = self.get_object()

        # 成功激活用户以后生成新的JWT并放到Cookie里
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(confirmation.email_address.user)
        token = jwt_encode_handler(payload)
        response.set_cookie('JWT', token)
        return response


class UserViewSets(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny, ]
    serializer_class = UserDetailsSerializer

    @action(methods=['get'], detail=True)
    def replies(self, request, pk=None):
        user = self.get_object()
        replies = user.reply_comments.filter(is_public=True, is_removed=False)
        serializer = FlatReplySerializer(replies, many=True)
        return Response(serializer.data)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated, OncePerDay, IsCurrentUser]
    )
    def checkin(self, request, pk=None):
        user = self.get_object()

        # 生成随机奖励
        random_amount = abs(random.gauss(10, 5))
        random_amount = math.ceil(random_amount)

        if random_amount == 0:
            random_amount += 1

        record = Record.objects.create(
            reward_type=0,
            coin_type=2,
            amount=random_amount,
            description='',
            user=user
        )
        serializer = BalanceSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
