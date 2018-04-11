from actstream.models import Follow
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.urls import reverse
from rest_framework import status
from rest_framework import test
from notifications.models import Notification
from actstream.models import Follow

from posts.models import Post
from users.models import User

from replies.models import Reply
from replies.moderation import ReplyModerator

reply_moderator = ReplyModerator(ReplyModerator)


class NotificationViewSetsTestCase(test.APITestCase):
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
            author=self.user
        )
        self.post_ct = ContentType.objects.get_for_model(self.post)
        self.post_id = self.post.id

        self.another_post = Post.objects.create(
            title='another title',
            author=self.another_user
        )
        self.another_post_ct = ContentType.objects.get_for_model(self.another_post)
        self.another_post_id = self.another_post.id

        self.site = Site.objects.create(name='test', domain='test.com')

        # 其他用户评论测试用户的文章
        self.reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.another_user,
            comment='reply',
        )

        # 测试用户评论其他用户的文章
        self.another_reply = Reply.objects.create(
            content_type=self.another_post_ct,
            object_pk=self.another_post_id,
            site=self.site,
            user=self.user,
            comment='reply',
        )

    def test_anonymous_user_can_not_get_notifications_method(self):
        # 未登录用户无法获取通知列表

        url = reverse('notifications-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_get_all_notifications_method(self):
        # 已登录用户可以获取到自己的通知列表

        url = reverse('notifications-list')
        data = {
            "unread": "all"
        }
        self.client.login(username='test', password='test')
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_get_notifications_not_others_method(self):
        # 已登录用户可以获取到自己的通知列表
        # 确认用户访问API获取的就是自己的通知列表，而不是别人的

        reply_moderator.notify(reply=self.reply, content_object=self.post, request=None)
        url = reverse('notifications-list')
        self.client.login(username='test', password='test')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['recipient'], self.user.id)

    def test_authenticated_user_can_get_single_notification_method(self):
        # 用户可以获取自己单条通知

        reply_moderator.notify(reply=self.reply, content_object=self.post, request=None)
        # reply = Reply.objects.first()
        notification = Notification.objects.first()
        url = reverse('notifications-detail', kwargs={'pk': notification.id})
        self.client.login(username='test', password='test')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_not_get_other_users_single_notification_method(self):
        # 用户无法通过API获取属于其它用户的单条通知

        reply_moderator.notify(reply=self.another_reply, content_object=self.another_post, request=None)
        notification = Notification.objects.first()
        url = reverse('notifications-detail', kwargs={'pk': notification.id})
        self.client.login(username='test', password='test')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_modify_single_notification_to_read_method(self):
        # 用户可以将自己的单条通知标为已读

        reply_moderator.notify(reply=self.reply, content_object=self.post, request=None)
        notification = Notification.objects.first()
        self.assertEqual(notification.unread, True)
        url = reverse('notifications-detail', kwargs={'pk': notification.id})
        self.client.login(username='test', password='test')
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification = Notification.objects.first()
        self.assertEqual(notification.unread, False)

    def test_authenticated_user_can_not_modify_other_users_single_notification_to_read_method(self):
        # 用户无法通过 API 将其它用户的通知标为已读

        reply_moderator.notify(reply=self.another_reply, content_object=self.another_post, request=None)
        notification = Notification.objects.first()
        self.assertEqual(notification.unread, True)
        url = reverse('notifications-detail', kwargs={'pk': notification.id})
        self.client.login(username='test', password='test')
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        notification = Notification.objects.first()
        self.assertEqual(notification.unread, True)

    def test_authenticated_user_can_delete_single_notification_method(self):
        # 用户可以将自己的单条通知删除

        reply_moderator.notify(reply=self.reply, content_object=self.post, request=None)
        notification = Notification.objects.first()
        self.assertEqual(notification.deleted, False)
        url = reverse('notifications-detail', kwargs={'pk': notification.id})
        self.client.login(username='test', password='test')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        notification = Notification.objects.first()
        self.assertEqual(notification.deleted, True)

    def test_authenticated_user_can_delete_other_user_single_notification_method(self):
        # 用户无法通过 API 将其它用户的单条通知删除

        reply_moderator.notify(reply=self.another_reply, content_object=self.another_post, request=None)
        notification = Notification.objects.first()
        self.assertEqual(notification.deleted, False)
        url = reverse('notifications-detail', kwargs={'pk': notification.id})
        self.client.login(username='test', password='test')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        notification = Notification.objects.first()
        self.assertEqual(notification.deleted, False)

    def test_authenticated_user_can_make_all_notification_to_read_method(self):
        # 用户可以将自己的全部通知标为已读

        reply_moderator.notify(reply=self.reply, content_object=self.post, request=None)
        notification = Notification.objects.first()
        self.assertEqual(notification.unread, True)  # 验证未读
        url = reverse('notifications-mark-all-as-read')
        self.client.login(username='test', password='test')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification = Notification.objects.first()
        self.assertEqual(notification.unread, False)  # 验证已读

    def test_authenticated_user_can_not_make_other_users_all_notification_to_read_method(self):
        # 用户可以将自己的全部通知标为已读

        reply_moderator.notify(reply=self.another_reply, content_object=self.another_post, request=None)
        notification = Notification.objects.first()
        self.assertEqual(notification.unread, True)  # 其他用户的通知 验证未读
        url = reverse('notifications-mark-all-as-read')
        self.client.login(username='test', password='test')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification = Notification.objects.first()
        self.assertEqual(notification.unread, True)  # 其他用户的通知 验证未读
