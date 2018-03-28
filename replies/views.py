from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
)
from django_comments import signals
from rest_framework import permissions
from .serializers import (
    ReplyCreationSerializer,
    TreeReplySerializer,
    FlatReplySerializer,
    FollowSerializer,
)

from .models import Reply


class ReplyCreateView(CreateAPIView):
    serializer_class = ReplyCreationSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):
        parent_reply = serializer.validated_data.get('parent')
        reply = serializer.save(user=self.request.user, parent=parent_reply)

        # 创建相应的 notification
        signals.comment_was_posted.send(
            sender=reply.__class__,
            comment=reply,
            request=self.request
        )


class FlatReplyListView(ListAPIView):
    """
    仅仅用于测试，并不需要对外暴露此 API
    """
    queryset = Reply.objects.all()
    serializer_class = FlatReplySerializer


class TreeReplyListView(ListAPIView):
    """
    仅仅用于测试，并不需要对外暴露此 API
    """
    queryset = Reply.objects.filter(parent__isnull=True)
    serializer_class = TreeReplySerializer


class ReplyLikeCreateView(CreateAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):
        reply = serializer.save(user=self.request.user)

        # 创建相应的 notification
        # signals.comment_was_posted.send(
        #     sender=reply.__class__,
        #     comment=reply,
        #     request=self.request
        # )
