from django_comments.moderation import CommentModerator
from django_comments.moderation import Moderator as DjangoCommentModerator
from notifications.signals import notify


class Moderator(DjangoCommentModerator):
    def post_save_moderation(self, sender, comment, request, **kwargs):
        model = comment.content_type.model_class()
        if model not in self._registry:
            return
        self._registry[model].notify(comment, comment.content_object, request)


class ReplyModerator(CommentModerator):
    def notify(self, reply, content_object, request):
        post_author = content_object.author

        if reply.parent:  # 回复的回复
            parent_user = reply.parent.user
            # 通知被回复的人，自己回复自己无需通知
            if parent_user != reply.user:
                reply_data = {
                    'recipient': parent_user,
                    'verb': 'respond',
                    'action_object': reply,
                    'target': content_object,
                }
                notify.send(sender=reply.user, **reply_data)

            if parent_user != content_object.author and post_author != reply.user:
                # 如果被回复的人不是帖子作者，且不是帖子作者自己的回复，帖子作者应该收到通知
                comment_data = {
                    'recipient': post_author,
                    'verb': 'reply',
                    'action_object': reply,
                    'target': content_object,
                }
                notify.send(sender=reply.user, **comment_data)
        else:
            # 如果是直接回复，且不是帖子作者自己回复，则通知帖子作者
            if post_author != reply.user:
                comment_data = {
                    'recipient': post_author,
                    'verb': 'reply',
                    'action_object': reply,
                    'target': content_object,
                }
                notify.send(sender=reply.user, **comment_data)


moderator = Moderator()
