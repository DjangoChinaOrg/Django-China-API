import os
import sys

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + '../')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django

django.setup()

from users.factories import UserFactory
from tags.factories import TagFactory
from replies.factories import PostReplyFactory
from posts.factories import PostFactory
from balance.factories import RecordFactory

if __name__ == '__main__':
    # TODO: delete db first then migrate
    user = UserFactory()
    print(user.username)

    tag = TagFactory()
    print(tag.name)

    reply = PostReplyFactory()
    print(reply.comment)

    post = PostFactory(tags=[tag])
    print(post.title)

    record = RecordFactory()
    print(record.amount)
