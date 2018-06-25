from django.apps import AppConfig


class RepliesConfig(AppConfig):
    name = 'replies'

    def ready(self):
        from .moderation import moderator
        from .moderation import ReplyModerator
        from posts.models import Post
        from actstream import registry
        registry.register(self.get_model('Reply'))
        registry.register(Post)
        moderator.register(Post, ReplyModerator)
