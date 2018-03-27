from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tags.models import Tag
from users.models import User


class TagTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='test',
                                             nickname='test')
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='admin@test.com',
                                                   password='admin',
                                                   nickname='admin')

    def test_admin_can_create_tag(self):
        """
        测试管理员可以添加标签
        """
        url = reverse('tag-list')
        data = {
            'name': 'test tag'
        }
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.get().creator, self.admin)
        self.assertEqual(Tag.objects.get().name, 'test tag')

    def test_unauthorized_user_cannot_create_tag(self):
        """
        测试没有权限用户无法添加标签
        """
        url = reverse('tag-list')
        data = {
            'name': 'test tag'
        }
        self.client.login(username='test', password='test')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_create_tag(self):
        """
        测试未登录用户无法添加标签
        """
        url = reverse('tag-list')
        data = {
            'name': 'test tag'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
