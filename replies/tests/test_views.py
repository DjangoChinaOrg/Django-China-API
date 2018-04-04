from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from rest_framework import status
from rest_framework.test import APITestCase
from notifications.models import Notification
from actstream.models import Follow

from posts.models import Post
from users.models import User
from ..models import Reply


class ReplyViewSetsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@test.com',
            password='test',
            nickname='test'
        )
        self.another_user = User.objects.create_user(
            username='another',
            email='another@test.com',
            password='another',
            nickname='another'
        )
        self.post = Post.objects.create(
            title='test title',
            author=self.another_user
        )
        self.post_ct = ContentType.objects.get_for_model(self.post)
        self.post_id = self.post.id

    def test_authenticated_user_can_create_reply(self):
        url = reverse('replies:create_reply')
        data = {
            "content_type": self.post_ct.id,
            "object_pk": self.post_id,
            "site": 1,
            "comment": "test comment",
            "submit_date": None,
            "ip_address": None,
            "parent": None,
        }
        self.client.login(username='test', password='test')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reply.objects.count(), 1)
        self.assertEqual(Reply.objects.get().comment, 'test comment')

        # 确定生成了通知
        self.assertEqual(Notification.objects.count(), 1)

    def test_anonymous_user_can_not_create_reply(self):
        url = reverse('replies:create_reply')
        data = {
            "content_type": self.post_ct.id,
            "object_pk": self.post_id,
            "site": 1,
            "comment": "test comment",
            "submit_date": None,
            "ip_address": None,
            "parent": None,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_support_post_method(self):
        url = reverse('replies:create_reply')
        data = {
            "content_type": self.post_ct.id,
            "object_pk": self.post_id,
            "site": 1,
            "comment": "test comment",
            "submit_date": None,
            "ip_address": None,
            "parent": None,
        }
        self.client.login(username='test', password='test')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ReplyLikeCreateViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@test.com',
            password='test',
            nickname='test'
        )
        self.post = Post.objects.create(
            title='test title',
            author=self.user
        )
        self.post_ct = ContentType.objects.get_for_model(self.post)
        self.post_id = self.post.id
        self.site = Site.objects.create(name='test', domain='test.com')
        self.reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='reply',
        )
        self.reply_ct = ContentType.objects.get_for_model(self.reply)
        self.reply_id = self.reply.id

    def test_authenticated_user_can_like_reply(self):
        url = reverse('replies:like_reply')
        data = {
            "content_type": self.reply_ct.id,
            "object_id": self.reply_id,
            "flag": "like",
        }
        self.client.login(username='test', password='test')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(Reply.objects.get().user, self.user)

        # 确定生成了通知
        self.assertEqual(Notification.objects.count(), 1)

    def test_anonymous_user_can_not_like_reply(self):
        url = reverse('replies:like_reply')
        data = {
            "content_type": self.reply_ct.id,
            "object_id": self.reply_id,
            "flag": "like",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_support_post_method(self):
        url = reverse('replies:like_reply')
        data = {
            "content_type": self.reply_ct.id,
            "object_pk": self.reply_id,
            "flag": "like",
        }
        self.client.login(username='test', password='test')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
