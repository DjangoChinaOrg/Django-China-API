from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.timezone import now, timedelta

from users.models import User
from posts.models import Post
from ..models import Reply


class RelyModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='test',
                                             nickname='test')
        self.post = Post.objects.create(title='test title', author=self.user)
        self.site = Site.objects.create(name='test', domain='test.com')
        self.post_ct = ContentType.objects.get_for_model(self.post)
        self.post_id = self.post.id

    def test_descendants(self):
        """测试以正确的顺序返回了全部回复"""
        self.root_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='root reply',
            submit_date=now()
        )
        self.child_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='child reply',
            parent=self.root_reply,
            submit_date=now() + timedelta(minutes=1)
        )

        self.another_child_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='another child reply',
            parent=self.root_reply,
            submit_date=now() + timedelta(minutes=2)
        )

        self.grandchild_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='grandchild reply',
            parent=self.child_reply,
            submit_date=now() + timedelta(minutes=3)
        )

        self.assertQuerysetEqual(
            self.root_reply.descendants(),
            [repr(o) for o in [self.child_reply, self.another_child_reply, self.grandchild_reply]]
        )
