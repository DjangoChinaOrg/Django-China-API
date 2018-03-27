import datetime

from django.utils.timezone import now
from django.db.models import Max, Count

from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets, pagination
from rest_framework.decorators import list_route
from rest_framework.response import Response

from .models import Post
from .serializers import PostSerializer
from .permissions import IsAdminAuthorOrReadOnly


class PostPagination(pagination.PageNumberPagination):
    page_size = 20


class PostViewSet(viewsets.ModelViewSet):
    # 所有非隐藏的帖子
    queryset = Post.public.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAdminAuthorOrReadOnly)
    pagination_class = PostPagination
    # 允许get post put方法
    http_method_names = ['get', 'post', 'put']
    filter_backends = (filters.DjangoFilterBackend,)
    #在post-list页面可以按标签字段过滤出特定标签下的帖子
    filter_fields = ('tags',)

    def perform_create(self, serializer):
        """
        因为author字段在PostSerializer里是ReadOnly，所以这里需要手动保存
        """
        serializer.save(author=self.request.user)

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
