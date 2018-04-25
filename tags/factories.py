# factories that automatically create user data
import factory

from users.factories import UserFactory

from .models import Tag


class TagFactory(factory.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: 'tag%s' % n)
    creator = factory.SubFactory(UserFactory, username='admin')
