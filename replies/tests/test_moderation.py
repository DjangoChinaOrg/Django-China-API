from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from notifications.models import Notification

from posts.models import Post
from users.models import User

from ..models import Reply
from ..moderation import ReplyModerator

reply_moderator = ReplyModerator(ReplyModerator)


class ModerationTestCase(TestCase):
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
        self.site = Site.objects.create(name='test', domain='test.com')
        self.post_ct = ContentType.objects.get_for_model(self.post)
        self.post_id = self.post.id

    def test_post_author_received_reply_notification(self):
        """帖子被回复后，且回复者不是作者，则作者收到通知"""
        reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.another_user,  # 回复者不是帖子作者
            comment='reply',
        )

        reply_moderator.notify(reply=reply, content_object=self.post, request=None)
        self.assertEqual(Notification.objects.count(), 1)

    def test_reply_self_do_not_received_notification(self):
        reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,  # 回复者是帖子作者
            comment='reply',
        )

        reply_moderator.notify(reply=reply, content_object=self.post, request=None)
        self.assertEqual(Notification.objects.count(), 0)

    def test_reply_others_reply_as_well_as_others_post(self):
        """回复他人回复且不是自己的帖子，他人和帖子作者收到通知"""
        user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='user',
            nickname='user'
        )

        reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.another_user,
            comment='reply',
        )

        new_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=user,
            comment='new reply',
            parent=reply,
        )

        reply_moderator.notify(reply=new_reply, content_object=self.post, request=None)
        self.assertEqual(Notification.objects.count(), 2)

    def test_reply_others_reply_but_self_post(self):
        """回复他人回复但是自己的帖子，他人收到通知"""
        reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.another_user,
            comment='reply',
        )

        new_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='new reply',
            parent=reply,
        )

        reply_moderator.notify(reply=new_reply, content_object=self.post, request=None)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(
            Notification.objects.get().recipient,
            reply.user
        )

    def test_reply_self_reply_as_well_as_self_post(self):
        """回复自己的回复和自己的帖子，没有任何通知"""
        reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,  # 回复者是帖子作者
            comment='reply',
        )

        new_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,  # 回复者是帖子作者
            comment='new reply',
            parent=reply,
        )

        reply_moderator.notify(reply=new_reply, content_object=self.post, request=None)
        self.assertEqual(Notification.objects.count(), 0)

    def test_reply_self_reply_but_others_post(self):
        """回复自己的回复和让人的帖子，帖子作者收到一条通知"""
        reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.another_user,  # 回复者是帖子作者
            comment='reply',
        )

        new_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.another_user,  # 回复者是帖子作者
            comment='new reply',
            parent=reply,
        )

        reply_moderator.notify(reply=new_reply, content_object=self.post, request=None)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(
            Notification.objects.get().recipient,
            self.post.author
        )
