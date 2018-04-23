import factory
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from posts.factories import PostFactory
from replies.models import Reply
from users.factories import UserFactory


class SiteFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'example_%s' % n)
    domain = factory.LazyAttribute(lambda o: '%s.com' % o.name)

    class Meta:
        model = Site


class BaseReplyFactory(factory.DjangoModelFactory):
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object))
    object_pk = factory.SelfAttribute('content_object.id')
    user = factory.SubFactory(UserFactory)
    site = factory.SubFactory(SiteFactory)
    comment = 'test comment'

    class Meta:
        model = Reply


class PostReplyFactory(BaseReplyFactory):
    content_object = factory.SubFactory(PostFactory)
