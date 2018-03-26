from django.apps import AppConfig


class RepliesConfig(AppConfig):
    name = 'replies'

    def ready(self):
        from .moderation import moderator
        from .moderation import ReplyModerator
        from posts.models import Post
        moderator.register(Post, ReplyModerator)
