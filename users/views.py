import math
import random

from allauth.account.views import ConfirmEmailView as AllAuthConfirmEmailView
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Sum
from django.utils import timezone
from rest_auth.registration.views import (
    LoginView, RegisterView, SocialConnectView, SocialLoginView)
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from balance.models import Record
from balance.permissions import IsCurrentUser, OncePerDay
from balance.serializers import BalanceSerializer
from posts.serializers import IndexPostListSerializer
from replies.serializers import FlatReplySerializer

from .models import User
from .permissions import IsVerified, NotPrimary
from .serializers import EmailAddressSerializer, UserDetailsSerializer


class RegisterViewCustom(RegisterView):
    """
    注册视图取消authentication_class一次避免CSRF校验
    """
    authentication_classes = ()


class LoginViewCustom(LoginView):
    """
    登陆视图取消authentication_class以此避免CSRF校验
    """
    authentication_classes = ()


class ConfirmEmailView(AllAuthConfirmEmailView):
    template_name = 'account/email_confirm.html'


class GitHubLogin(SocialLoginView):
    authentication_classes = ()
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client
    callback_url = getattr(settings, 'SOCIAL_LOGIN_GITHUB_CALLBACK_URL')


class GitHubConnect(SocialConnectView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client
    callback_url = getattr(settings, 'SOCIAL_LOGIN_GITHUB_CALLBACK_URL')


class UserViewSets(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    # TODO: 用户的email等隐私信息需要特殊处理
    permission_classes = [AllowAny, ]
    serializer_class = UserDetailsSerializer
    lookup_value_regex = '[0-9]+'

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsCurrentUser()]
        return super().get_permissions()

    @action(methods=['get'], detail=True, serializer_class=FlatReplySerializer)
    def replies(self, request, pk=None):
        user = self.get_object()
        replies = user.reply_comments.filter(is_public=True, is_removed=False)
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(replies, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=True, serializer_class=IndexPostListSerializer)
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
            page = self.paginate_queryset(posts.filter(hidden=True))
            if page is not None:
                serializer = self.get_serializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(
                posts.filter(hidden=True),
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)

        page = self.paginate_queryset(posts.filter(hidden=False))
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            posts.filter(hidden=False),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated, OncePerDay, IsCurrentUser],
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

    @action(methods=['get'], detail=True,
            permission_classes=[permissions.IsAuthenticated, IsCurrentUser], )
    def checked(self, request, pk=None):
        user = self.get_object()
        today_start = timezone.now().replace(hour=0, minute=0, second=0)
        today_end = timezone.now().replace(hour=23, minute=59, second=59)
        checked = user.record_set.filter(created_time__gt=today_start, created_time__lt=today_end).exists()
        return Response({'checked': checked})


class MugshotUploadView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (FileUploadParser,)

    def post(self, request, filename):
        if 'file' not in request.FILES:
            return Response({
                'file': 'No avatar file selected.'
            }, status=status.HTTP_400_BAD_REQUEST)
        file_obj = request.FILES['file']

        limit_kb = 2048
        if file_obj.size > limit_kb * 1024:
            return Response({
                'file': 'File size is too large.'
            }, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.mugshot.name
        user.mugshot.save(filename, file_obj)
        user.save()
        user.refresh_from_db()
        return Response({'mugshot_url': user.mugshot.url}, status=200)


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
            return super(EmailAddressViewSet, self).get_permissions()

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
