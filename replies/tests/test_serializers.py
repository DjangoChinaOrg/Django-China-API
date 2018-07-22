from pprint import pprint

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase
from django.utils.timezone import now, timedelta

from posts.models import Post
from users.models import User

from ..models import Reply
from ..serializers import TreeRepliesSerializer


class ReplySerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test',
                                             email='test@test.com',
                                             password='test',
                                             nickname='test')
        self.post = Post.objects.create(title='test title', author=self.user)
        self.site = Site.objects.create(name='test', domain='test.com')
        self.post_ct = ContentType.objects.get_for_model(self.post)
        self.post_id = self.post.id

    def tearDown(self):
        pass

    def test_tree_reply_serializer(self):
        # - root
        # - - child
        # - - - grand child
        # - - another_child
        # - another root
        # - - another root child
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

        self.another_root_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='another root reply',
            submit_date=now()
        )

        self.another_root_child_reply = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='another root child reply',
            parent=self.another_root_reply,
            submit_date=now() + timedelta(minutes=1)
        )
        request = RequestFactory().get('/')
        request.user = self.user
        replies = self.post.replies.filter(is_public=True, is_removed=False, parent__isnull=True)
        serializer = TreeRepliesSerializer(replies, many=True, context={'request': request})

        pprint(serializer.data)
