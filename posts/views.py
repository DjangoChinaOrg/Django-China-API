import datetime

from django.db.models import Count, Max
from django.utils.timezone import now
from django_filters import rest_framework as filters
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from replies.serializers import TreeRepliesSerializer
from tags.models import Tag
from .models import Post
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (
    IndexPostListSerializer,
    PopularPostSerializer,
    PostDetailSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = IndexPostListSerializer.setup_eager_loading(
        Post.public.annotate(
            latest_reply_time=Max('replies__submit_date')
        ).order_by('-pinned', '-latest_reply_time', '-created'),
        select_related=IndexPostListSerializer.SELECT_RELATED_FIELDS,
        prefetch_related=IndexPostListSerializer.PREFETCH_RELATED_FIELDS
    )
    serializer_class = IndexPostListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAdminAuthorOrReadOnly)
    # 允许get post put方法
    http_method_names = ['get', 'post', 'put', 'patch']
    filter_backends = (filters.DjangoFilterBackend,)
    # 在post-list页面可以按标签字段过滤出特定标签下的帖子
    filter_fields = ('tags',)

    def retrieve(self, request, *args, **kwargs):
        """
        重写帖子详情页，这里使用PostDetailSerializer，
        而不是默认的IndexPostListSerializer
        """
        instance = self.get_object()
        instance.increase_views()
        instance.refresh_from_db()
        serializer = PostDetailSerializer(instance, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        重写创建帖子方法，使用PostDetailSerializer
        """
        serializer = PostDetailSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        保存tags和author，同时验证tag的数量
        tags和author在PostSerializer里是read_only
        """
        tags_data = self.request.data.get('tags')
        tags = []
        if not tags_data:
            raise serializers.ValidationError(detail={'标签': '请选择至少一个标签'})
        elif len(tags_data) > 3:
            raise serializers.ValidationError(detail={'标签': '最多可以选择三个标签'})
        for name in tags_data:
            try:
                tag = Tag.objects.get(name=name)
                tags.append(tag)
            except Exception:
                raise serializers.ValidationError(detail={'标签': '标签不存在'})
        serializer.save(author=self.request.user, tags=tags)

    def update(self, request, *args, **kwargs):
        """
        更新帖子的方法，包括put和patch，
        """
        partial = kwargs.pop('partial', False)
        tags_data = request.data.get('tags')
        if partial and tags_data is None:
            pass
        elif not tags_data:
            raise serializers.ValidationError(detail={'标签': '请选择至少一个标签'})
        elif len(tags_data) > 3:
            raise serializers.ValidationError(detail={'标签': '最多可以选择三个标签'})
        instance = self.get_object()
        serializer = PostDetailSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        """
        执行更新
        """
        data = {}
        tags = []
        # 标签，隐藏，置顶，加精这些字段都是read_only，
        # 因此这些字段在修改时需要手动来保存
        tags_data = self.request.data.get('tags')
        # 如果用户不是管理，则无需提取这些字段
        if self.request.user.is_staff:
            hidden = self.request.data.get('hidden')
            pinned = self.request.data.get('pinned')
            highlighted = self.request.data.get('highlighted')
            if hidden is not None:
                data['hidden'] = hidden
            if pinned is not None:
                data['pinned'] = pinned
            if highlighted is not None:
                data['highlighted'] = highlighted
        if tags_data:
            for name in tags_data:
                try:
                    tag = Tag.objects.get(name=name)
                    tags.append(tag)
                except Exception:
                    raise serializers.ValidationError(detail={'标签': '标签不存在'})
            data['tags'] = tags
        serializer.save(**data)

    @action(detail=False, serializer_class=PopularPostSerializer)
    def popular(self, request):
        """
        返回48小时内评论次数最多的帖子
        """
        popular_posts = PopularPostSerializer.setup_eager_loading(
            Post.public.annotate(
                num_replies=Count('replies'),
                latest_reply_time=Max('replies__submit_date')
            ).filter(
                num_replies__gt=0,
                latest_reply_time__gt=(now() - datetime.timedelta(days=2)),
                latest_reply_time__lt=now()
            ).order_by('-num_replies', '-latest_reply_time')[:10],
            select_related=PopularPostSerializer.SELECT_RELATED_FIELDS
        )

        # return paginated queryset as response data if paginator exists
        self.paginator.page_size = 10
        page = self.paginate_queryset(popular_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(popular_posts, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, serializer_class=TreeRepliesSerializer)
    def replies(self, request, pk=None):
        post = self.get_object()
        replies = post.replies.filter(is_public=True, is_removed=False, parent__isnull=True)
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(replies, many=True, context={'request': request})
        return Response(serializer.data)
