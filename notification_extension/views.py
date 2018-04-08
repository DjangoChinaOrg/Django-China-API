from rest_framework import permissions, viewsets, pagination, mixins
from notifications.models import Notification
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status

from .serializers import NotificationSerializer
from .filters import NotificationFilter


class NotificationPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "page"


class NotificationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination
    permission_classes = [permissions.IsAuthenticated, ]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ('timestamp',)
    filter_class = NotificationFilter  # 过滤器

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).active()

    def perform_destroy(self, instance):
        pk = self.kwargs['pk']
        instance = Notification.objects.get(id=pk)
        instance.deleted = True
        instance.save()

    def perform_update(self, serializer):
        serializer.update()

    def update(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        instance = Notification.objects.get(id=pk)
        instance.unread = False
        instance.save()
        return Response(status=status.HTTP_202_ACCEPTED)
