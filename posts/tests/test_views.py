from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post
from tags.models import Tag
from users.models import User


class PostTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='test',
                                             nickname='test')
        self.another_user = User.objects.create_user(username='test2',
                                             email='test2@test.com',
                                             password='test2',
                                             nickname='test2')
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='admin@admin.com',
                                                   password='admin123',
                                                   nickname='admin')
        self.tag1 = Tag.objects.create(name='test tag1', creator=self.user)
        self.tag2 = Tag.objects.create(name='test tag2', creator=self.user)
        self.tag3 = Tag.objects.create(name='test tag3', creator=self.user)
        self.tag4 = Tag.objects.create(name='test tag4', creator=self.user)

    def test_authenticated_user_can_create_post(self):
        """
        测试登录用户可以发帖子,
        """
        url = reverse('post-list')
        data = {
            "title": "test title",
            "body": "test test test",
            "tags": ['test tag1', 'test tag2', 'test tag3']
        }
        data2 = {
            "title": "test title",
            "body": "test test test",
        }
        self.client.login(username='test', password='test')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().author, self.user)
        self.assertEqual(Post.objects.get().body, 'test test test')
        self.assertEqual(Post.objects.get().title, 'test title')
        self.assertEqual(Post.objects.get().tags.count(), 3)
        self.assertEqual(Post.objects.get().pinned, False)
        self.assertEqual(Post.objects.get().highlighted, False)
        self.assertEqual(Post.objects.get().hidden, False)

        # 当提交的数据不完整时
        response = self.client.post(url, data2, formant='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_user_cannot_create_post(self):
        """
        测试未登录用户 不可以发帖子
        """
        url = reverse('post-list')
        data = {
            "title": "test title",
            "body": "test test test",
            "tags": ['test tag1', 'test tag2', 'test tag3']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_tags_quantity(self):
        """
        测试帖子标签的数量 大于等于1， 小于等于3
        以及标签不存在的情况
        测试方法 包括POST, PUT, PATCH
        """
        self.post = Post.objects.create(title='this is a test',
                                        body='this is a test',
                                        author=self.user
                                        )
        self.post.tags.add(self.tag1)
        url1 = reverse('post-list')
        url2 = reverse('post-detail', kwargs={'pk': self.post.pk})
        data1 = {
            "title": "test title",
            "body": "test test test",
            "tags": []
        }
        data2 = {
            "title": "test title",
            "body": "test test test",
            "tags": ['test tag1', 'test tag2', 'test tag3', 'test tag4']
        }
        data3 = {
            "tags": []
        }
        data4 = {
            "title": "test title",
            "body": "test test test",
            "tags": ["tag does not exist"]
        }
        self.client.login(username='test', password='test')
        response = self.client.post(url1, data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url1, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url1, data4, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(url2, data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.patch(url2, data3, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.patch(url2, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.patch(url2, data4, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_author_admin_can_edit_post(self):
        """
        测试只有管理员和作者可以编辑帖子,
        同时作者无法修改hidden, highlighted, pinned字段
        """
        self.post = Post.objects.create(title='this is a test',
                                        body='this is a test',
                                        author=self.user
                                        )
        self.post.tags.add(self.tag1)
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        data1 = {
            "title": "hello",
            "body": "hello world",
            "tags": ['test tag1', 'test tag2', 'test tag3']
        }
        data2 = {
            "title": "hello",
            "body": "hello world",
            "tags": ['test tag1', 'test tag2', 'test tag3'],
            "pinned": True,
            "highlighted": True
        }
        data3 = {
            "pinned": False,
            "highlighted": False
        }
        data4 = {
            "hidden": True,
        }
        # 管理员
        self.client.login(username='admin', password='admin123')
        response = self.client.put(url, data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 测试管理 置顶, 加精帖子
        response = self.client.put(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get().pinned, True)
        self.assertEqual(Post.objects.get().highlighted, True)
        response = self.client.patch(url, data3, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get().pinned, False)
        self.client.logout()

        # 作者
        self.client.login(username='test', password='test')
        response = self.client.put(url, data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 作者加精 置顶 隐藏
        response = self.client.put(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get().pinned, False)
        self.assertEqual(Post.objects.get().highlighted, False)
        response = self.client.patch(url, data4, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.get().hidden, False)
        self.client.logout()

        # 其他用户
        self.client.login(username='test2', password='test2')
        response = self.client.put(url, data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.put(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data3, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        # 管理员隐藏帖子
        self.client.login(username='admin', password='admin123')
        response = self.client.patch(url, data4, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('post-list'), format='json')
        self.assertEqual(response.data['count'], 0)

    def test_index_post_list(self):
        """
        测试首页列表数量，以及分页情况
        """
        for i in range(5):
            self.post = Post.objects.create(title='this is a test',
                                            body='this is a test',
                                            author=self.user
                                            )
            self.post.tags.add(self.tag1)
        url = reverse('post-list')
        self.client.login(username='test', password='test')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        url = reverse('post-list') + '?page=2'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        for i in range(16):
            self.post = Post.objects.create(title='this is a test',
                                            body='this is a test',
                                            author=self.user
                                            )
            self.post.tags.add(self.tag1)

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 21)
        self.assertEqual(response.data['next'], None)

    def test_post_detail(self):
        """
        测试帖子详情
        """
        self.post = Post.objects.create(title='this is a test',
                                        body='this is a test',
                                        author=self.user
                                        )
        self.post.tags.add(self.tag1)
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['title'], 'this is a test')
        self.assertEqual(response.data['body'], 'this is a test')
        self.assertEqual(response.data['author']['nickname'], 'test')

        url = reverse('post-detail', kwargs={'pk': self.post.pk + 1})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
