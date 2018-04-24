import os
import sys
import random

BASE_DIR = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django

django.setup()

from users.factories import UserFactory
from users.models import User
from tags.factories import TagFactory
from tags.models import Tag
from replies.factories import PostReplyFactory, SiteFactory
from replies.models import Reply
from posts.factories import PostFactory
from posts.models import Post
from balance.factories import RecordFactory

from allauth.account.models import EmailAddress
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from faker import Faker

if __name__ == '__main__':
    site = SiteFactory()
    c = APIClient()
    fake = Faker()
    # 生成 5 个用户
    UserFactory.create_batch(5)
    print('users created...')

    # 生成 5 个标签
    user = UserFactory(username='admin')
    TagFactory.create_batch(5, creator=user)
    print('tags created...')

    tags = list(Tag.objects.all())
    users = list(User.objects.all())

    # 每个用户发布一定量的帖子
    for user in users:
        post_count = random.randint(5, 10)

        for i in range(post_count):
            tag_count = random.randint(1, 3)
            tag_sample = random.sample(tags, tag_count)
            PostFactory(author=user, tags=tag_sample)

        # 绑定一个 email
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=True,
            primary=True
        )
        # 获得一定的财富
        RecordFactory.create_batch(random.randint(0, 3), user=user)

    print('posts posted...')

    posts = list(Post.objects.all())

    # 随机选择一些用户对每个帖子进行回复，使用 client 发送请求，
    # 这样回复时会生成相应通知
    for post in posts:
        post_ct = ContentType.objects.get_for_model(post)
        post_id = post.id
        url = reverse('reply-list')

        user_sample = random.sample(users, random.randint(0, 5))
        for user in user_sample:
            data = {
                "content_type": post_ct.id,
                "object_pk": post_id,
                "site": 1,
                "comment": fake.text(max_nb_chars=200, ext_word_list=None)
            }
            c.force_login(user)
            c.post(url, data, format='json')

    print('post replies created...')

    # 再随机选择一些用户对某些回复进行回复
    for i in range(2):
        replies = list(Reply.objects.all())
        for reply in replies:
            indicator = random.randint(0, 2)
            if indicator:  # 以 1/3 的概率回复
                continue
            post = reply.content_object
            post_ct = ContentType.objects.get_for_model(post)
            post_id = post.id
            url = reverse('reply-list')
            user_sample = random.sample(users, random.randint(1, 3))

            for user in user_sample:
                data = {
                    "content_type": post_ct.id,
                    "object_pk": post_id,
                    "site": 1,
                    "comment": fake.text(max_nb_chars=200, ext_word_list=None),
                    "parent": reply.id
                }
                c.force_login(user)
                c.post(url, data, format='json')
    print('reply replies created...')

    # 再随机选择一些用户对回复进行点赞
    replies = list(Reply.objects.all())
    for i in range(2):
        for reply in replies:
            indicator = random.randint(0, 2)
            if indicator:  # 以 1/3 的概率回复
                continue
            url = reverse('reply-like', kwargs={'pk': reply.id})
            user_sample = random.sample(users, random.randint(1, 3))

            for user in user_sample:
                data = {
                    "content_type": reply.ctype_id,
                    "object_id": reply.id,
                    "flag": "like",
                }
                c.force_login(user)
                c.post(url, data, format='json')
    print('liked!')
    print('done...!')