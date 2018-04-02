from rest_framework import permissions, viewsets, pagination, mixins
from notifications.models import Notification
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import NotificationSerializer
from .filters import NotificationFilter


class NotificationPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "page"


class NotificationViewSet(mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination
    permission_classes = [permissions.IsAuthenticated, ]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ('timestamp', )
    # filter_class = NotificationFilter  # 过滤器

    # def get_queryset(self):
    #     # TODO 全部通知 已读通知 和 未读通知
    #     return Notification.objects.filter(recipient=self.request.user)

    queryset = Notification.objects.all()

    def perform_destroy(self, instance):
        instance.delete()

    def perform_update(self, serializer):
        serializer.update()
