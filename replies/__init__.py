default_app_config = 'replies.apps.RepliesConfig'


def get_model():
    from .models import Reply
    return Reply
