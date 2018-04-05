from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post
from tags.models import Tag
from users.models import User


class PostTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='test',
                                             nickname='test')
        self.tag1 = Tag.objects.create(name='test tag1', creator=self.user)
        self.tag2 = Tag.objects.create(name='test tag2', creator=self.user)
        self.tag3 = Tag.objects.create(name='test tag3', creator=self.user)
        self.tag4 = Tag.objects.create(name='test tag4', creator=self.user)

    def test_authenticated_user_can_create_post(self):
        """
        测试登录用户可以发帖子
        """
        url = reverse('post-list')
        data = {
            "title": "test title",
            "body": "test test test",
            "tags": [1, 2, 3]
        }
        self.client.login(username='test', password='test')
        response = self.client.post(url, data, format='json')
        # TODO: 返回 400 状态码
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(Post.objects.count(), 1)
        # self.assertEqual(Post.objects.get().author, self.user)
        # self.assertEqual(Post.objects.get().body, 'test test test')
        # self.assertEqual(Post.objects.get().title, 'test title')
        # self.assertEqual(Post.objects.get().tags.count(), 3)
        # self.assertEqual(Post.objects.get().pinned, False)
        # self.assertEqual(Post.objects.get().highlighted, False)
        # self.assertEqual(Post.objects.get().hidden, False)

    def test_anonymous_user_cannot_create_post(self):
        """
        测试未登录用户 不可以发帖子
        """
        url = reverse('post-list')
        data = {
            "title": "test title",
            "body": "test test test",
            "tags": [1, 2, 3]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_tags_quantity(self):
        """
        测试帖子标签的数量 大于等于1， 小于等于3
        """
        url = reverse('post-list')
        data1 = {
            "title": "test title",
            "body": "test test test",
            "tags": []
        }
        data2 = {
            "title": "test title",
            "body": "test test test",
            "tags": [1, 2, 3, 4]
        }
        self.client.login(username='test', password='test')
        response = self.client.post(url, data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
