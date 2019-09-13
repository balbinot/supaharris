import factory
from faker import Factory
from django.conf import settings

from accounts.models import UserModel

faker = Factory.create("en_UK")


class UserModelFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserModel
        django_get_or_create = ("email",)

    email = factory.LazyAttribute(lambda _: faker.email())
    first_name = factory.LazyAttribute(lambda _: faker.first_name())
    last_name = factory.LazyAttribute(lambda _: faker.last_name())

    is_active = True
    is_staff = False
    is_superuser = False


class AdminFactory(UserModelFactory):
    is_staff = True
    is_superuser = True
