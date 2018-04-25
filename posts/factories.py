import factory

from users.factories import UserFactory

from .models import Post


class PostFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence')
    body = factory.Faker('text')
    author = factory.SubFactory(UserFactory)

    class Meta:
        model = Post

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for tag in extracted:
                self.tags.add(tag)
