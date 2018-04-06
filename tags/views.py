from collections import OrderedDict

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Tag
from .permissions import TagPermissionOrReadOnly
from .serializers import TagSerializer


class TagPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('tags', data)
        ]))


class TagViewSet(viewsets.ModelViewSet):
    """
    标签列表按照帖子数量来排序的
    """
    queryset = Tag.objects.annotate(num_posts=Count('post')).order_by('-num_posts')
    serializer_class = TagSerializer
    permission_classes = (TagPermissionOrReadOnly,)
    pagination_class = TagPagination
    http_method_names = ['get', 'post', 'patch']

    def perform_create(self, serializer):
        """
        因为author字段在PostSerializer里是ReadOnly，所以这里需要手动保存
        """
        serializer.save(creator=self.request.user)
