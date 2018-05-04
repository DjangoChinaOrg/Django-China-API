from actstream.models import Follow
from django.db.utils import IntegrityError
from django_comments import signals
from notifications.signals import notify
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from replies.permissions import NotSelf
from replies.serializers import (FollowSerializer,
                                 ReplyCreationSerializer)
from replies.models import Reply


class ReplyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ReplyCreationSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Reply.objects.filter(is_public=True, is_removed=False)

    def perform_create(self, serializer):
        parent_reply = serializer.validated_data.get('parent')
        reply = serializer.save(user=self.request.user, parent=parent_reply)

        # 创建相应的 notification
        signals.comment_was_posted.send(
            sender=reply.__class__,
            comment=reply,
            request=self.request
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[NotSelf, permissions.IsAuthenticated],
        serializer_class=FollowSerializer,
    )
    def like(self, request, pk=None):
        reply = self.get_object()

        if self.request.method == 'POST':
            try:
                follow = Follow.objects.create(
                    user=self.request.user,
                    content_type=reply.ctype,
                    object_id=reply.id,
                    flag='like',
                )
            except IntegrityError:
                return Response(
                    {'detail': '已经赞过'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowSerializer(follow, context={'request': request})
            # 创建相应的 notification
            data = {
                'recipient': reply.user,
                'verb': 'like',
                'action_object': reply.content_object,
                'target': reply
            }
            notify.send(sender=self.request.user, **data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            Follow.objects.filter(
                user=self.request.user,
                content_type=reply.ctype_id,
                object_id=reply.id,
                flag='like'
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
