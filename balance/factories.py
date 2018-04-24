import math
import random

import factory

from users.factories import UserFactory

from .models import Record


class RecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = Record

    reward_type = 0
    coin_type = 2
    user = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def amount(self):
        random_amount = abs(random.gauss(10, 5))
        random_amount = math.ceil(random_amount)

        if random_amount == 0:
            random_amount += 1

        return random_amount
