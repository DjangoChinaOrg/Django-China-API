from django.db.models import Count

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Tag
from .serializers import TagSerializer
from .permissions import TagPermissionOrReadOnly


class TagPagination(PageNumberPagination):
    page_size = 10


class TagViewSet(viewsets.ModelViewSet):
    """
    标签按照帖子数量来排序的
    """
    queryset = Tag.objects.annotate(num_posts=Count('post')).order_by('-num_posts')
    serializer_class = TagSerializer
    permission_classes = (TagPermissionOrReadOnly,)
    pagination_class = TagPagination
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        """
        因为author字段在PostSerializer里是ReadOnly，所以这里需要手动保存
        """
        serializer.save(creator=self.request.user)
