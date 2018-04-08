from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Tag
from .permissions import TagPermissionOrReadOnly
from .serializers import TagSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (TagPermissionOrReadOnly,)
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        """
        因为author字段在PostSerializer里是ReadOnly，所以这里需要手动保存
        """
        serializer.save(creator=self.request.user)

    @action(detail=False)
    def popular(self, request):
        """
        返回帖子数量最多的前10标签
        """
        tags = self.get_queryset().annotate(
            num_posts=Count('post')).order_by('-num_posts')[:10]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)
