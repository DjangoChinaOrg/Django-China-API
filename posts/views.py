import datetime
from collections import OrderedDict

from django.utils.timezone import now
from django.db.models import Max, Count

from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets, pagination, serializers
from rest_framework.decorators import list_route
from rest_framework.response import Response

from .models import Post
from tags.models import Tag
from .serializers import PostSerializer
from .permissions import IsAdminAuthorOrReadOnly


class PostPagination(pagination.PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('posts', data)
        ]))


class PostViewSet(viewsets.ModelViewSet):
    # 所有非隐藏的帖子
    queryset = Post.public.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAdminAuthorOrReadOnly)
    pagination_class = PostPagination
    # 允许get post put方法
    http_method_names = ['get', 'post', 'put', 'patch']
    filter_backends = (filters.DjangoFilterBackend,)
    # 在post-list页面可以按标签字段过滤出特定标签下的帖子
    filter_fields = ('tags',)

    def perform_create(self, serializer):
        """
        保存tags和author，同时验证tag的数量
        tags和author在PostSerializer里是read_only
        """
        tags = []
        tags_data = self.request.data.get('tags')
        if not tags_data:
            raise serializers.ValidationError("请至少选择一个标签")
        if len(tags_data) > 3:
            raise serializers.ValidationError("最多可以选择3个标签")
        for name in tags_data:
            try:
                tag = Tag.objects.get(name=name)
                tags.append(tag)
            except Exception:
                raise serializers.ValidationError("标签不存在")
        serializer.save(author=self.request.user, tags=tags)

    def perform_update(self, serializer):
        super(PostViewSet, self).perform_update(serializer)
        tags = []
        tags_data = self.request.data.get('tags')
        if not tags_data:
            raise serializers.ValidationError("请至少选择一个标签")
        if len(tags_data) > 3:
            raise serializers.ValidationError("最多可以选择3个标签")
        for name in tags_data:
            try:
                tag = Tag.objects.get(name=name)
                tags.append(tag)
            except Exception:
                raise serializers.ValidationError("标签不存在")
        serializer.save(tags=tags)


    @list_route()
    def popular_posts(self, request):
        """
        返回48小时内评论次数最多的帖子
        """
        popular_posts = Post.public.annotate(
            num_replies=Count('replies'),
            latest_reply_time=Max('replies__submit_date')
        ).filter(
            num_replies__gt=0,
            latest_reply_time__gt=(now() - datetime.timedelta(days=2)),
            latest_reply_time__lt=now()
        ).order_by('-num_replies', '-latest_reply_time')[:10]
        serializer = self.get_serializer(popular_posts, many=True)
        return Response(serializer.data)
