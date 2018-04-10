import math
import random

from allauth.account.views import ConfirmEmailView as AllAuthConfirmEmailView
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from django.db.models import Sum
from rest_auth.registration.views import LoginView, RegisterView, SocialLoginView
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from balance.api.permissions import IsCurrentUser, OncePerDay
from balance.api.serializers import BalanceSerializer
from balance.models import Record
from posts.serializers import IndexPostListSerializer
from replies.api.serializers import FlatReplySerializer

from .models import User
from .permissions import IsVerified, NotPrimary
from .serializers import EmailAddressSerializer, UserDetailsSerializer


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


class LoginViewCustom(LoginView):
    """
    登陆视图取消authentication_class以此避免CSRF校验
    """
    authentication_classes = ()


class RegisterViewCustom(RegisterView):
    """
    注册视图取消authentication_class以此避免CSRF校验
    """
    authentication_classes = ()


class GitHubLogin(SocialLoginView):
    """
    GitHub登陆视图
    """
    adapter_class = GitHubOAuth2Adapter
    authentication_classes = ()


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

    @action(methods=['get'], detail=True)
    def posts(self, request, pk=None):
        user = self.get_object()
        posts = user.post_set.all()
        hidden = self.request.query_params.get('hidden')
        if hidden:
            if not self.request.user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            # 只有用户自己可以查看被隐藏的帖子
            if user != self.request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = IndexPostListSerializer(posts.filter(hidden=True), many=True, context={'request': request})
            return Response(serializer.data)

        serializer = IndexPostListSerializer(posts.filter(hidden=False), many=True, context={'request': request})
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

    @action(methods=['get'], detail=True)
    def balance(self, request, pk=None):
        user = self.get_object()
        user_treasure = user.record_set.values('coin_type').annotate(Sum('amount'))
        return Response(user_treasure)


class EmailAddressViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = EmailAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), NotPrimary()]
        else:
            return super().get_permissions()

    def get_queryset(self):
        return self.request.user.emailaddress_set.all()

    def perform_create(self, serializer):
        email = serializer.save(user=self.request.user)
        email.send_confirmation(request=self.request)

    @action(methods=['post'], detail=True,
            permission_classes=[permissions.IsAuthenticated, IsVerified])
    def set_primary(self, request, pk=None):
        email = self.get_object()
        success = email.set_as_primary()

        if success:
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def reverify(self, request, pk=None):
        email = self.get_object()
        email.send_confirmation(request=self.request)

        return Response(status=status.HTTP_200_OK)
