from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tags.models import Tag
from users.models import User
from posts.models import Post


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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_duplicate_tags(self):
        """
        测试没有重复的标签
        """
        """
        测试管理员可以添加标签
        """
        self.tag = Tag.objects.create(name='test tag',
                                      creator=self.admin
                                      )
        url = reverse('tag-list')
        data = {
            'name': 'test tag'
        }
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_popular_tags(self):
        """
        测试热门标签
        """
        self.post1 = Post.objects.create(title='this is a test1',
                                        body='this is a test',
                                        author=self.admin
                                        )
        self.post2 = Post.objects.create(title='this is a test2',
                                        body='this is a test',
                                        author=self.admin
                                        )
        self.post3 = Post.objects.create(title='this is a test3',
                                         body='this is a test',
                                         author=self.admin
                                         )
        self.tag1 = Tag.objects.create(name='test tag1',
                                      creator=self.admin
                                      )
        self.tag2 = Tag.objects.create(name='test tag2',
                                      creator=self.admin
                                      )
        self.tag3 = Tag.objects.create(name='test tag3',
                                      creator=self.admin
                                      )
        self.post1.tags.add(self.tag1, self.tag2)
        self.post2.tags.add(self.tag2, self.tag3, self.tag1)
        self.post3.tags.add(self.tag2)
        url = reverse('tag-popular')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data[0]['name'], 'test tag2')
        self.assertEqual(response.data[1]['name'], 'test tag1')
        self.assertEqual(response.data[2]['name'], 'test tag3')
