from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APITestCase
from notifications.models import Notification

from posts.models import Post
from users.models import User
from tags.models import Tag
from .models import Reply


class AccountTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='test',
                                             nickname='test')
        self.another_user = User.objects.create_user(username='another',
                                                     email='another@test.com',
                                                     password='another',
                                                     nickname='another')
        # self.tag = Tag.objects.create(name='test tag', creator=self.user)
        self.post = Post.objects.create(title='test title', author=self.another_user)
        self.post_type_id = ContentType.objects.get_for_model(self.post).id
        self.post_id = self.post.id

    def test_authenticated_user_can_create_reply(self):
        "登录用户可以创建回复"
        url = reverse('replies:create_reply')
        data = {
            "content_type": self.post_type_id,
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
            "content_type": self.post_type_id,
            "object_pk": self.post_id,
            "site": 1,
            "comment": "test comment",
            "submit_date": None,
            "ip_address": None,
            "parent": None,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_support_post_method(self):
        url = reverse('replies:create_reply')
        data = {
            "content_type": self.post_type_id,
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
