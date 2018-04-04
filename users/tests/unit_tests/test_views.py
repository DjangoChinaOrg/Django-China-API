from rest_framework import test
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from rest_framework.reverse import reverse
from rest_framework import status

from replies.models import Reply
from replies.api.serializers import FlatReplySerializer
from posts.models import Post
from ...models import User


class UserViewSetTestCase(test.APITestCase):
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

        self.site = Site.objects.create(name='test', domain='test.com')
        self.post = Post.objects.create(
            title='test title',
            author=self.another_user
        )
        self.post_ct = ContentType.objects.get_for_model(self.post)
        self.post_id = self.post.id

    def test_return_user_replies(self):
        reply1 = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='reply1',
        )
        reply2 = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.user,
            comment='reply2',
            parent=reply1
        )
        reply3 = Reply.objects.create(
            content_type=self.post_ct,
            object_pk=self.post_id,
            site=self.site,
            user=self.another_user,
            comment='reply3',
            parent=reply1
        )

        url = reverse('user-replies', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            FlatReplySerializer(
                self.user.reply_comments.filter(is_public=True, is_removed=False),
                many=True
            ).data
        )
