from rest_framework.generics import (
    CreateAPIView,
)
from django_comments import signals
from rest_framework import permissions
from .serializers import ReplyCreationSerializer


class ReplyCreationView(CreateAPIView):
    serializer_class = ReplyCreationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def perform_create(self, serializer):
        parent_reply = serializer.validated_data.get('parent')
        reply = serializer.save(user=self.request.user, parent=parent_reply)
        signals.comment_was_posted.send(
            sender=reply.__class__,
            comment=reply,
            request=self.request
        )
